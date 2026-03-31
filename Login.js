function Login({ onLoginSuccess }) {
    const [user, setUser] = React.useState(""); 
    const [status, setStatus] = React.useState("");

    async function getWebData(e) {
        e.preventDefault();
        try {
            const response = await fetch(`http://localhost:8000/Login/${user}`);
            if (response.ok) {
                const tempData = await response.json();
                if (tempData && tempData[0]?.Count > 0) {
                    setStatus("Successfully Logged In!");
                    onLoginSuccess(user, status); 
                } else {
                    setStatus("Invalid Username");
                }
            }
        } catch (error) {
            console.error("Connection error:", error);
            setStatus("Server Error");
        }
    }

    return (
        <div>
            <form onSubmit={getWebData}>
                <label> Enter Your username to access the website:
                    <input type="text" value={user} onChange={(e) => setUser(e.target.value)} />
                </label>
                <button type="submit">Login</button>
            </form>
            <p>{status}</p>
        </div>
    );
}