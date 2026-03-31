function AddUser({ setStatus }) {
    const [user, setUser] = React.useState("");

    async function sendUserDataToPython(e) {
        e.preventDefault();
        try {
            const response = await fetch('http://localhost:8000/AddUser', {
                method: "POST", 
                headers: {'Content-Type': "application/json"}, 
                body: JSON.stringify({"username": user})
            });
            const success = await response.json();
            setStatus(success ? "Successfully Added User!" : "Error Adding User!");
        } catch (error) {
            setStatus("Server Error");
        }
    }

    return (
        <form onSubmit={sendUserDataToPython}>
            <label> Enter Your Username:
                <input type="text" value={user} onChange={(e) => setUser(e.target.value)}/>
            </label>
            <button type="submit">Add</button>
        </form>
    );
}

async function DelUser(username) {
    const user = username

        try {
            const response = await fetch('http://localhost:8000/DelUser', {
                method: "POST", 
                headers: {'Content-Type': "application/json"}, 
                body: JSON.stringify({"username": user})
            });
            const success = await response.json();
            console.log(success ? "User Deleted!" : "Error Deleting User!");
        } catch (error) {
            console.log(error)
        }
}