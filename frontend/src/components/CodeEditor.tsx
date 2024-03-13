import {useState} from "react";
import './CodeEditor.css';

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

            <button onClick={() => console.log(code)}>Submit</button>
        </div>
    );
}