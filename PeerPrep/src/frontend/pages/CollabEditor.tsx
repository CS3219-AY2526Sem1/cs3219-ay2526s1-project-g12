import { CodeEditor } from "../components/Collab/CodeEditor";
import { ProblemPanel } from "../components/Collab/ProblemPanel";
import { TopBar } from "../components/Collab/TopBar";

export default function CollabEditor() {
  return (
    <div className="min-h-screen flex flex-col px-20 py-10">
      <TopBar />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-10 justify-center overflow-hidden">
        <div className="card shadow-sm border-1 border-base-200 p-10 overflow-y-auto">
          <ProblemPanel />
        </div>

        <div className="col-span-2 card shadow-sm border-1 border-base-200 p-10">
          <div className="w-full overflow-visible">
            <CodeEditor />
          </div>
        </div>
      </div>
    </div>
  );
}
