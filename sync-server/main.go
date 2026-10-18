package main

import (
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"sync"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

type SyncRecord struct {
	DeviceID      string    `json:"device_id"`
	EncryptedData string    `json:"encrypted_data"` // AES-256-GCM ciphertext (Base64)
	DataType      string    `json:"data_type"`      // bookmarks, passwords, history, tabs, extensions
	Version       int64     `json:"version"`
	UpdatedAt     time.Time `json:"updated_at"`
}

type SyncServer struct {
	db       *sql.DB
	clients  map[string]map[chan []byte]bool // chainHash -> set of client channels
	clientsM sync.RWMutex
}

func NewSyncServer(dbPath string) (*SyncServer, error) {
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return nil, err
	}

	createTableQuery := `
	CREATE TABLE IF NOT EXISTS sync_records (
		chain_id TEXT NOT NULL,
		data_type TEXT NOT NULL,
		device_id TEXT NOT NULL,
		encrypted_data TEXT NOT NULL,
		version INTEGER NOT NULL,
		updated_at DATETIME NOT NULL,
		PRIMARY KEY (chain_id, data_type)
	);
	CREATE INDEX IF NOT EXISTS idx_chain ON sync_records(chain_id);
	`
	if _, err := db.Exec(createTableQuery); err != nil {
		return nil, err
	}

	return &SyncServer{
		db:      db,
		clients: make(map[string]map[chan []byte]bool),
	}, nil
}

func hashToken(token string) string {
	h := sha256.Sum256([]byte(token))
	return hex.EncodeToString(h[:])
}

func (s *SyncServer) handlePush(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	auth := r.Header.Get("X-Zenith-Sync-Token")
	if auth == "" {
		http.Error(w, "Unauthorized: X-Zenith-Sync-Token missing", http.StatusUnauthorized)
		return
	}
	chainID := hashToken(auth)

	var record SyncRecord
	if err := json.NewDecoder(r.Body).Decode(&record); err != nil {
		http.Error(w, "Bad request payload", http.StatusBadRequest)
		return
	}

	record.UpdatedAt = time.Now().UTC()
	query := `
	INSERT INTO sync_records (chain_id, data_type, device_id, encrypted_data, version, updated_at)
	VALUES (?, ?, ?, ?, ?, ?)
	ON CONFLICT(chain_id, data_type) DO UPDATE SET
		device_id = excluded.device_id,
		encrypted_data = excluded.encrypted_data,
		version = excluded.version,
		updated_at = excluded.updated_at;
	`
	_, err := s.db.Exec(query, chainID, record.DataType, record.DeviceID, record.EncryptedData, record.Version, record.UpdatedAt)
	if err != nil {
		log.Printf("DB error on push: %v", err)
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"version": record.Version,
		"synced_at": record.UpdatedAt,
	})
}

func (s *SyncServer) handlePull(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	auth := r.Header.Get("X-Zenith-Sync-Token")
	if auth == "" {
		http.Error(w, "Unauthorized: X-Zenith-Sync-Token missing", http.StatusUnauthorized)
		return
	}
	chainID := hashToken(auth)

	rows, err := s.db.Query("SELECT device_id, encrypted_data, data_type, version, updated_at FROM sync_records WHERE chain_id = ?", chainID)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var records []SyncRecord
	for rows.Next() {
		var rec SyncRecord
		if err := rows.Scan(&rec.DeviceID, &rec.EncryptedData, &rec.DataType, &rec.Version, &rec.UpdatedAt); err == nil {
			records.append(records, rec)
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"records": records,
	})
}

func (s *SyncServer) handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":  "healthy",
		"service": "Zenith Sync Relay",
		"version": "1.0.0",
		"time":    time.Now().UTC(),
	})
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "zenith_sync.db"
	}

	server, err := NewSyncServer(dbPath)
	if err != nil {
		log.Fatalf("Failed to initialize Zenith Sync Server: %v", err)
	}

	http.HandleFunc("/health", server.handleHealth)
	http.HandleFunc("/api/v1/sync/push", server.handlePush)
	http.HandleFunc("/api/v1/sync/pull", server.handlePull)

	fmt.Printf("==================================================\n")
	fmt.Printf(" Zenith Browser E2EE Sync Relay Server             \n")
	fmt.Printf(" Listening on: http://0.0.0.0:%s                 \n")
	fmt.Printf(" Database: %s                                     \n")
	fmt.Printf(" Zero-Knowledge Encryption: AES-256-GCM           \n")
	fmt.Printf("==================================================\n")

	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}
