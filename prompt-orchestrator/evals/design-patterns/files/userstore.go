package store

type UserStore interface {
	Get(id string) (*User, error)
	Save(u *User) error
}

type PostgresUserStore struct{ db *sql.DB }

func (s *PostgresUserStore) Get(id string) (*User, error) { /* ... */ return nil, nil }
func (s *PostgresUserStore) Save(u *User) error          { /* ... */ return nil }
