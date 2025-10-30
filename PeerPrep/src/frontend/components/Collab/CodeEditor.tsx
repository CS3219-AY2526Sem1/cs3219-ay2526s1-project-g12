import { useEffect, useRef } from "react";
import { MonacoBinding } from "y-monaco";
import * as Y from "yjs";
import { WebrtcProvider } from "y-webrtc";
import Editor, { type OnMount } from "@monaco-editor/react";
import * as monaco from "monaco-editor";

type CodeEditorProps = {
  matchDetail: string;
  userId: string;
};

export function CodeEditor({ matchDetail, userId }: CodeEditorProps) {
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);

  useEffect(() => {
    const ydoc = new Y.Doc();
    const provider = new WebrtcProvider(`room-${matchDetail}`, ydoc);
    const ytext = ydoc.getText("monaco");

    if (editorRef.current) {
      const model = editorRef.current.getModel();
      if (model) {
        new MonacoBinding(
          ytext,
          model,
          new Set([editorRef.current]),
          provider.awareness,
        );
      }
    }

    // save code to localStorage periodically
    const saveInterval = setInterval(() => {
      const code = editorRef.current?.getValue() || "";
      localStorage.setItem("collab_code", code);
    }, 3000);

    return () => {
      clearInterval(saveInterval);
      provider.destroy();
      ydoc.destroy();
    };
  }, [matchDetail]);

  const handleEditorDidMount: OnMount = (editor) => {
    editorRef.current = editor;
  };

  return (
    <Editor
      height="70vh"
      theme="light"
      language="python"
      defaultValue={`class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        `}
      onMount={handleEditorDidMount}
      options={{
        scrollBeyondLastLine: false,
        minimap: { enabled: false },
        lineNumbers: "on",
        lineNumbersMinChars: 4,
        renderLineHighlight: "all",
        wordWrap: "on",
        automaticLayout: true,
        scrollbar: {
          vertical: "hidden",
          handleMouseWheel: true,
        },
      }}
    />
  );
}
