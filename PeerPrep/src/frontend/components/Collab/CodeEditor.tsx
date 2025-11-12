import { useEffect, useRef } from 'react';
import { MonacoBinding } from 'y-monaco';
// import * as Y from 'yjs';
// import { WebrtcProvider } from 'y-webrtc';
import Editor, { type OnMount } from '@monaco-editor/react';
import * as monaco from 'monaco-editor';
import { useCollab } from '../../context/CollabProviderContext';

type CodeEditorProps = {
  // matchDetail: string;
  userId: string;
  defaultCode: string;
  isReconnecting?: boolean;
};

export function CodeEditor({
  // matchDetail: roomId,
  userId,
  defaultCode,
  isReconnecting = false,
}: CodeEditorProps) {
  const { ydoc, provider, roomId } = useCollab();
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const modelRef = useRef<monaco.editor.ITextModel | null>(null);
  const bindingRef = useRef<MonacoBinding | null>(null);
  const saveIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  // const providerRef = useRef<WebrtcProvider | null>(null);
  // const ydocRef = useRef<Y.Doc | null>(null);

  const handleEditorDidMount: OnMount = (editor, monacoNs) => {
    if (!ydoc || !provider) {
      console.warn('Collab provider not ready yet');
      return;
    }

    editorRef.current = editor;

    // Get shared text
    const ytext = ydoc.getText('monaco');

    // Load initial code
    const savedCode = localStorage.getItem('collab_code') || '';
    const initialCode = isReconnecting && savedCode ? savedCode : defaultCode;
    // Seed Yjs doc with initial code only if empty
    if (ytext.length === 0 && initialCode) {
      ytext.insert(0, initialCode);
    }

    // Create a Monaco model explicitly
    const uri = monacoNs.Uri.parse(`inmemory://model/${roomId}.py`);
    let model = monacoNs.editor.getModel(uri);
    if (!model) {
      model = monacoNs.editor.createModel('', 'python', uri);
    }
    editor.setModel(model);
    modelRef.current = model;

    // Initialize WebRTC provider
    // const provider = new WebrtcProvider(`room-${roomId}`, ydoc, {
    //   signaling: [
    //     'ws://localhost:4444',
    //   ],
    //   peerOpts: {
    //     config: {
    //       iceServers: [{ urls: ['stun:stun.l.google.com:19302'] }],
    //     },
    //   },
    // });
    // providerRef.current = provider;

    // Awareness info (so cursors are colored per user)
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
    bindingRef.current = binding;

    // Periodically save current code to localStorage every 3s
    saveIntervalRef.current = setInterval(() => {
      const code = editor.getValue() || '';
      localStorage.setItem('collab_code', code);
    }, 3000);

    // Cleanup when editor unmounts
    editor.onDidDispose(() => {
      if (saveIntervalRef.current) clearInterval(saveIntervalRef.current);
      binding.destroy();
      // provider.destroy();
      // ydoc.destroy();
      model?.dispose();
      bindingRef.current = null;
    });
  };

  // Cleanup when unmounting
  useEffect(() => {
    return () => {
      if (saveIntervalRef.current) clearInterval(saveIntervalRef.current);
      // providerRef.current?.destroy();
      // ydocRef.current?.destroy();
      bindingRef.current?.destroy();
      modelRef.current?.dispose();
      localStorage.removeItem('collab_code');
    };
  }, []);

  // If defaultCode changes (e.g. after reconnection) and the editor is empty, repopulate it.
  useEffect(() => {
    if (editorRef.current && defaultCode) {
      const currentValue = editorRef.current.getValue();
      if (!currentValue?.trim()) {
        editorRef.current.setValue(defaultCode);
      }
    }
  }, [defaultCode]);

  return (
    <Editor
      height="70vh"
      theme="light"
      language="python"
      defaultValue={defaultCode ?? ''}
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
