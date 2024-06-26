import { useState } from "react";
import './CodeEditor.css';
import axios from 'axios';

import {
    MaterialReactTable,
    MRT_Table,
    type MRT_ColumnDef, useMaterialReactTable
} from "material-react-table";

type FunctionType = {
    name: string,
    exec_time: number
}

const generateTable = (functions: Array<FunctionType>) => {
    let columns: Array<MRT_ColumnDef<FunctionType>> = [
        { accessorKey: 'name', header: "Function Name" },
        { accessorKey: 'exec_time', header: "Execution Time" }
    ];
    let data = functions;

    // minimalistic table
    return (
        <MaterialReactTable
            columns={columns}
            data={data}
            muiTableProps={{
                size: "small"
                }
            }
        />
    );

}

export default function CodeEditor(): JSX.Element {

    let [userCode, setUserCode] = useState("");
    let [outputText, setOutputText] = useState("Nothing yet...");
    let [wcetFunctions, setWcetFunctions] = useState<Array<FunctionType>>([]);
    let [wcetText, setWcetText] = useState<string | null>(null);

    function submitCode(userCode: string): void {
        axios.post("http://localhost:8000/api/analyze", {
            code: userCode
        }).then((response) => {
            setOutputText(response.data.llvm);
            console.log("WCET Functions:", response.data.wcet_functions);

            let function_list: Array<FunctionType> = Object.entries(response.data.wcet_functions).map(([name, exec_time]) => ({
                name,
                exec_time: exec_time as number
            }));
            setWcetFunctions(function_list);

            setWcetText(response.data.wcet_total)
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
            <div id="output">
                <h3>Output:</h3>
                <div id="function-table">
                    {generateTable(wcetFunctions)}
                </div>
                <div id="wcet">
                    <h3>WCET:</h3>
                    <p>WCET: {wcetText} CPU Cycles</p>
                </div>
            </div>
        </div>
    );
}
