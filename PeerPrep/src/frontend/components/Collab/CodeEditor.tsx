import { useEffect, useRef } from "react";
import { MonacoBinding } from "y-monaco";
import * as Y from "yjs";
import { WebrtcProvider } from "y-webrtc";
import Editor, { type OnMount } from "@monaco-editor/react";
import * as monaco from "monaco-editor";

export function CodeEditor() {
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);

  useEffect(() => {
    const ydoc = new Y.Doc();
    const provider = new WebrtcProvider("peerprep-room", ydoc);
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

    return () => {
      provider.destroy();
      ydoc.destroy();
    };
  }, []);

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
