import {useState} from "react";
import './CodeEditor.css';
import axios from 'axios';

export default function CodeEditor() : any {

    let [userCode, setUserCode] = useState("test");
    let [output, setOutput] = useState("Nothing yet...");

    function submitCode(userCode: string) : void {
    axios.post("http://localhost:8000/api/analyze", {
        code: userCode
    }).then((response) => {
        setOutput(response.data.code);
    }).catch((error) => {
        console.log(error);
    });
}

    return (
        <div id="code-editor-div">
            <textarea
            id="code-editor"
            rows={30}
            cols={200}
            placeholder="Enter your code here..."
            value={userCode}
            onChange={(e) => setUserCode(e.target.value)}
            />
            <button id="submit-button" onClick={() => submitCode(userCode)}>Submit</button>
            <h3>Output:</h3>
            <pre id="outputText">{output}</pre>
        </div>
    );
}