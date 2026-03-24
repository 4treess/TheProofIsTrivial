CREATE TABLE Users (
    username varchar(255) PRIMARY KEY
);

CREATE TABLE Proofs (
    proposition varchar(255) PRIMARY KEY,
    result varchar(8192),
    creator varchar(255) REFERENCES Users
);