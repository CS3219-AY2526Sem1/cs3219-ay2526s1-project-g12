import { useLocation, useNavigate } from 'react-router-dom';
import { CodeEditor } from '../components/Collab/CodeEditor';
import { ProblemPanel } from '../components/Collab/ProblemPanel';
import { TopBar } from '../components/Collab/TopBar';
import { ToastContainer, toast } from 'react-toastify';
import { useEffect, useRef, useState } from 'react';
import { apiClient } from '../api/ApiClient';

interface ConnectResponse {
  message: string;
}

export default function CollabEditor() {
  const navigate = useNavigate();
  const location = useLocation();
  const matchState = location.state as
    | { matchDetails: string; userId: string; partnerId: string }
    | undefined;

  if (!matchState || !matchState.matchDetails || !matchState.userId) {
    toast.error('Missing match data. Returning to lobby...');
    navigate('/matching');
    return null;
  }

  const { matchDetails, userId, partnerId } = matchState;
  const wsRef = useRef<WebSocket | null>(null);
  const heartbeatRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const [problem, setProblem] = useState({
    title: 'Loading...',
    description: '',
    code_template: '',
    solution_sample: '',
    difficulty: '',
    category: '',
  });

  const reconnectRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const retryCountRef = useRef<number>(0);
  const [isReconnecting, setIsReconnecting] = useState(false);

  useEffect(() => {
    let isUnmounted = false;

    const connectWS = () => {
      try {
        const ws = new WebSocket('ws://localhost:8000/ws/fe');
        wsRef.current = ws;

        ws.onopen = async () => {
          retryCountRef.current = 0;
          toast.dismiss('reconnect-toast');

          if (isReconnecting) {
            toast.success('✅ Reconnected successfully!');
            // Notify backend of reconnection
            console.log('User id:', userId);
            await fetch('http://localhost:8000/cs/reconnect', {
              method: 'POST',
              credentials: 'include',
              headers: {
                'Content-Type': 'application/json',
                'X-User-ID': userId,
              },
            }).catch(() => console.warn('Reconnect API failed (ignored)'));
            setIsReconnecting(false);
          } else {
            toast.success('Connected to collaboration room');
          }

          const res = await apiClient.request<ConnectResponse>(
            `/cs/connect/${matchDetails}`,
            {
              credentials: 'include',
              method: 'GET',
              headers: { 'X-User-ID': userId },
            }
          );
          if (res.data && res.data.message) {
            try {
              const message = JSON.parse(res.data.message);
              console.log('Problem data:', message);
              setProblem(message);
            } catch {
              console.warn('Invalid problem JSON');
            }
          }

          startHeartbeat();
        };

        ws.onmessage = (e) => {
          const data = JSON.parse(e.data);
          console.log('📩 Message:', data);

          if (data.message === 'partner_left') {
            toast.error('Your partner left the session');
          }
        };

        ws.onclose = () => {
          stopHeartbeat();
          if (!isUnmounted) handleReconnect();
        };
      } catch (error) {
        console.error('WebSocket connection error:', error);
        handleReconnect();
      }
    };

    const handleReconnect = () => {
      if (retryCountRef.current >= 5) {
        toast.error(
          'Failed to reconnect after several attempts. Returning to lobby...'
        );
        navigate('/matching');
        return;
      }

      retryCountRef.current += 1;
      const delay = 5000; // 5 seconds
      setIsReconnecting(true);

      if (!toast.isActive('reconnect-toast')) {
        toast.info(
          `Connection lost. Reconnecting in ${delay / 1000}s... (Attempt ${retryCountRef.current}/5)`,
          {
            toastId: 'reconnect-toast',
            autoClose: false,
            closeOnClick: false,
            draggable: false,
            position: 'top-center',
          }
        );
      } else {
        toast.update('reconnect-toast', {
          render: `Connection lost. Reconnecting in ${delay / 1000}s... (Attempt ${retryCountRef.current}/5)`,
        });
      }

      reconnectRef.current = setTimeout(() => {
        toast.dismiss('reconnect-toast');
        connectWS();
      }, delay);
    };

    connectWS();
    return () => {
      isUnmounted = true;
      wsRef.current?.close();
      stopHeartbeat();
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
    };
  }, [matchDetails, userId]);

  const startHeartbeat = () => {
    stopHeartbeat();
    heartbeatRef.current = setInterval(() => {
      wsRef.current?.send(
        JSON.stringify({
          user_id: userId,
          match_id: matchDetails,
          message: 'heartbeat',
        })
      );
    }, 60_000);
  };

  const stopHeartbeat = () => {
    if (heartbeatRef.current) {
      clearInterval(heartbeatRef.current);
      heartbeatRef.current = null;
    }
  };

  const handleExit = async () => {
    try {
      await fetch(`http://localhost:8000/cs/terminate/${matchDetails}`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', 'X-User-ID': userId },
        body: JSON.stringify({
          user_id: userId,
          match_id: matchDetails,
          message: 'terminate',
          code: localStorage.getItem('collab_code') || '',
        }),
      });
      toast.success('Session ended');
      navigate('/matching');
    } catch {
      toast.error('Error exiting session');
    }
  };

  return (
    <div className="min-h-screen flex flex-col px-20 py-10">
      <TopBar onExit={handleExit} />

      {isReconnecting && (
        <div className="bg-yellow-100 text-yellow-800 text-center p-2 rounded mb-4 animate-pulse">
          ⚠️ Connection lost — attempting to reconnect...
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-10 justify-center overflow-hidden">
        <div className="card shadow-sm border-1 border-base-200 p-10 overflow-y-auto">
          <ProblemPanel problem={problem} />
        </div>

        <div className="col-span-2 card shadow-sm border-1 border-base-200 p-10">
          <div className="w-full overflow-visible">
            <CodeEditor
              matchDetail={matchDetails}
              userId={userId}
              defaultCode={problem.code_template}
              isReconnecting={isReconnecting}
            />
          </div>
        </div>
      </div>

      <ToastContainer />
    </div>
  );
}
