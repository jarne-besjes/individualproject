import {useState} from "react";
import './CodeEditor.css';
import axios from 'axios';

function submitCode(code: string) {
    axios.post("http://localhost:8000/api/analyze", {
        code: code
    }).then((response) => {
        console.log(response);
    }).catch((error) => {
        console.log(error);
    });
}

export default function CodeEditor() : any {

    let [code, setCode] = useState("test");

    return (
        <div id="code-editor-div">
            <textarea
            id="code-editor"
            rows={30}
            cols={200}
            placeholder="Enter your code here..."
            value={code}
            onChange={(e) => setCode(e.target.value)}
            />

            <button onClick={() => submitCode(code)}>Submit</button>
        </div>
    );
}