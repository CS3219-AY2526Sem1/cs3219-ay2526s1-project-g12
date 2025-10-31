import { useEffect, useRef } from 'react';
import { MonacoBinding } from 'y-monaco';
import * as Y from 'yjs';
import { WebrtcProvider } from 'y-webrtc';
import Editor, { type OnMount } from '@monaco-editor/react';
import * as monaco from 'monaco-editor';

type CodeEditorProps = {
  matchDetail: string;
  userId: string;
  defaultCode: string;
  isReconnecting?: boolean;
};

export function CodeEditor({
  matchDetail,
  userId,
  defaultCode,
  isReconnecting = false,
}: CodeEditorProps) {
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const providerRef = useRef<WebrtcProvider | null>(null);
  const ydocRef = useRef<Y.Doc | null>(null);
  const saveIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Cleanup when unmounting
  useEffect(() => {
    return () => {
      if (saveIntervalRef.current) clearInterval(saveIntervalRef.current);
      providerRef.current?.destroy();
      ydocRef.current?.destroy();

      localStorage.removeItem("collab_code");
    };
  }, []);

  const handleEditorDidMount: OnMount = (editor, monacoNs) => {
    editorRef.current = editor;

    // Create a Yjs document and shared text
    const ydoc = new Y.Doc();
    const ytext = ydoc.getText('monaco');
    ydocRef.current = ydoc;

    // Load initial code
    const savedCode = localStorage.getItem("collab_code") || "";
    const initialCode = isReconnecting && savedCode ? savedCode : defaultCode;
    // Seed Yjs doc with initial code only if empty
    if (ytext.length === 0 && initialCode) {
      ytext.insert(0, initialCode);
    }

    // Create a Monaco model explicitly
    const uri = monacoNs.Uri.parse(`inmemory://model/${matchDetail}.py`);
    let model = monacoNs.editor.getModel(uri);
    if (!model) {
      model = monacoNs.editor.createModel('', 'python', uri);
    }
    editor.setModel(model);

    // Initialize WebRTC provider
    const provider = new WebrtcProvider(`room-${matchDetail}`, ydoc, {
      signaling: [
        'ws://localhost:4444', // local signaling server
        // "ws://pp-signaling-svc:4444" // docker network
      ],
      peerOpts: {
        config: {
          iceServers: [{ urls: ['stun:stun.l.google.com:19302'] }],
        },
      },
    });
    providerRef.current = provider;

    // Awareness (presence info)
    provider.awareness.setLocalStateField('user', {
      id: userId,
      color: `#${Math.floor(Math.random() * 16777215).toString(16)}`,
    });

    // Bind Monaco ↔ Yjs
    const binding = new MonacoBinding(
      ytext,
      model,
      new Set([editor]),
      provider.awareness
    );

    // Debug listeners
    // provider.on("status", (event: { status: string }) => {
    //   console.log(`[y-webrtc] Status: ${event.status}`);
    // });
    provider.on('peers', (event: { added: string[]; removed: string[] }) => {
      console.log(
        `[y-webrtc] Peers changed. Added:`,
        event.added,
        'Removed:',
        event.removed
      );
    });
    provider.awareness.on(
      'update',
      (event: { added: any[]; updated: any[]; removed: any[] }) => {
        console.log('[y-webrtc] Awareness update:', event);
      }
    );

    // Periodically save current code to localStorage every 3s
    saveIntervalRef.current = setInterval(() => {
      const code = editor.getValue() || '';
      localStorage.setItem('collab_code', code);
    }, 3000);

    // Cleanup when editor unmounts
    editor.onDidDispose(() => {
      if (saveIntervalRef.current) clearInterval(saveIntervalRef.current);
      binding.destroy();
      provider.destroy();
      ydoc.destroy();
      model?.dispose();
    });
  };

  return (
    <Editor
      height="70vh"
      theme="light"
      language="python"
      // defaultValue={`class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        `}
      onMount={handleEditorDidMount}
      options={{
        scrollBeyondLastLine: false,
        minimap: { enabled: false },
        lineNumbers: 'on',
        lineNumbersMinChars: 4,
        renderLineHighlight: 'all',
        wordWrap: 'on',
        automaticLayout: true,
        scrollbar: {
          vertical: 'hidden',
          handleMouseWheel: true,
        },
      }}
    />
  );
}
