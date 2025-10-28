import { CodeEditor } from "../components/Collab/CodeEditor";
import { ProblemPanel } from "../components/Collab/ProblemPanel";
import { TopBar } from "../components/Collab/TopBar";

export function CollabEditor() {
    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            <TopBar />

            <div className="flex flex-1 overflow-hidden p-6 gap-4">
                <div className="w-1/3 bg-white shadow-md rounded-2xl p-6 overflow-y-auto">
                    <ProblemPanel />
                </div>

                <div className="flex-1 bg-white shadow-md rounded-2xl p-4">
                    <CodeEditor />
                </div>
            </div>
        </div>
    );
}
