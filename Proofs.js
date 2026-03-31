function GetProof({ username, setStatus }) {
    const [proofs, setProofs] = React.useState([]);
    const [proposition, setProposition] = React.useState("");
    let stat = ""

    async function getWebData(e) {
        e.preventDefault();
        try {
            const response = await fetch(`http://localhost:8000/Proof/${proposition}`);
            let data = await response.json();
            if(Array.isArray(data) && data.length === 0){
                const successful = await AddProof(proposition, username)
                if (successful){
                    const response = await fetch(`http://localhost:8000/Proof/${proposition}`);
                    data = await response.json();
                }
            }

            setProofs(data);

        } catch (error) {
            console.error("Fetch error", error);
        }
    }

    return (
        <div>
            <form onSubmit={getWebData}>
                <label>
                    Enter in the proof you would like to generate:    
                    <input type="text" value={proposition} onChange={(e) => setProposition(e.target.value)} placeholder="Proposition Name"/>
                    <button type="submit">Generate</button>
                </label>
            </form> 
            {proofs.map((item, i) => (
                <p key={i}><strong>Claim:</strong> {item.proposition}<br/><strong>Proof:</strong> {item.result}</p>
            ))}
        </div>
    );
}

function GetProofs({ username, setStatus}) {
    const [proofs, setProofs] = React.useState([]);

    async function fetchAll() {
        try {
            const response = await fetch(`http://localhost:8000/Proofs/${username}`);
            const data = await response.json();
            setProofs(data);
        } catch (error) { console.error(error); }
    }

    return (
        <div>
            <button onClick={fetchAll}>Click To Retrieve Your Proofs</button>
            {proofs.map((item, i) => (
                <p key={i}>{item.creator}'s Proof #{i + 1}: <br/>Claim: {item.proposition} <br/>Proof: {item.result}<br/><a href="#" onClick={(e) => {e.preventDefault; DelProof(item.proposition, item.creator)}}>Delete Proof #{i + 1}</a><br/></p>
            ))}
        </div>
    );
}

async function AddProof(proposition, username) {
    let tempData = 0;

    try {
        const response = await fetch('http://localhost:8000/Proof', {method: "POST", headers: {'Content-Type': "application/json"}, body: JSON.stringify({"proposition": proposition, "result": "", "creator": username})});
        if(response.ok){
            tempData = await response.json();
            console.log("Retrieved The following from the server: ", tempData);
        } else {
            console.error("Error Connecting to server: ", response.status);
        }
    } catch (error) {
        console.error("Could not connect to the server! ", error);
    }

    return tempData
}

async function DelProof(proof, username) {
    let tempData = 0;

    try {
        const response = await fetch('http://localhost:8000/DelProof', {method: "POST", headers: {'Content-Type': "application/json"}, body: JSON.stringify({"proposition": proof, "result": "", "creator": username})});
        if(response.ok){
            tempData = await response.json();
            console.log("Retrieved The following from the server: ", tempData);
        } else {
            console.error("Error Connecting to server: ", response.status);
        }
    } catch (error) {
        console.error("Could not connect to the server! ", error);
    }
    return tempData
}