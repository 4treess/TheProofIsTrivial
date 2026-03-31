function App() {
    const [status, setStatus] = React.useState("Idle");
    const [username, setUsername] = React.useState("\0");

    if (username !== "\0") {
        return (
            <div>
                <h1>Welcome, <a href="https://youtu.be/xvFZjo5PgG0?si=v3olJo6kLQGr37Fg" style={{textDecoration: "none", color: "black"}}>{username}!</a></h1><a href="">Sign Out</a>
                <GetProof username={username} /> 
                <hr />
                <GetProofs username={username} />
                <a href="#" onClick={(e) => {e.preventDefault; DelUser(username); setUsername("\0")}} style={{fontSize: "8px"}}>Delete User</a>
            </div>
        );
    }

    return (
        <div>
            <h1>The Proof Is Trivial</h1>
            <Login onLoginSuccess={(name, stat) => {setStatus(stat); setUsername(name);}} />
            <hr />
            <p>New here?</p>
            <AddUser setStatus={setStatus} />
            <p>Status: {status}</p>
        </div>
    );
}