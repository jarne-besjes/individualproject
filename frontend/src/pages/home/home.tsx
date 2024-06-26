import CodeEditor from "../../components/CodeEditor";
import './code-editor.css';
import './home.css';
import logo from '../../logo.svg';

export default function Home() {
    return (
        <div id="home">
        <div id="logo">
            <img src={logo} className="CompLogo" alt="logo" />
        </div>
        <div id="code-editor-div">
            <h1>Complexity Analyser:</h1>
            <CodeEditor></CodeEditor>
        </div>
    </div>
)

}