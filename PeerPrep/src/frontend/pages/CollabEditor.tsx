import { useLocation, useNavigate } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import { useEffect, useRef, useState } from 'react';
import { useMatchTimer } from '../hooks/useMatchTimer';
import { collabApi } from '../api/CollaborationApi';
import { CollabProvider } from '../context/CollabProviderContext';
import { CollabSession } from '../components/Collab/CollabSession';

function getCookie(name: string): string | null {
  if (typeof document === 'undefined') {
    return null;
  }
  const nameEQ = name + '=';
  const ca = document.cookie.split(';');
  console.log('Cookies:', document.cookie);
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) === 0) {
      return c.substring(nameEQ.length, c.length);
    }
  }
  return null;
}
export default function CollabEditor() {
  const navigate = useNavigate();
  const location = useLocation();
  const matchState = location.state as
    | { matchDetails: string; userId: string }
    | undefined;

  if (!matchState || !matchState.matchDetails || !matchState.userId) {
    toast.error('Missing match data. Returning to lobby...');
    navigate('/matching');
    return null;
  }

  const { matchDetails, userId } = matchState;
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
  const [partnerName, setPartnerName] = useState('Your Partner');

  const reconnectRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const retryCountRef = useRef<number>(0);
  const [isReconnecting, setIsReconnecting] = useState(false);
  const { minutes, seconds } = useMatchTimer(true, 0, undefined, false);

  useEffect(() => {
    let isUnmounted = false;
    const token = getCookie('access_token') || '';

    const connectWS = () => {
      try {
        const url = new URL(import.meta.env.VITE_WS_GATEWAY_URL);
        url.searchParams.append('token', token);
        console.log('Connecting to WS URL:', url.toString());
        const ws = new WebSocket(url.toString());
        wsRef.current = ws;

        ws.onopen = async () => {
          retryCountRef.current = 0;
          toast.dismiss('reconnect-toast');

          if (isReconnecting) {
            toast.success('Reconnected successfully!');
            // Notify backend of reconnection
            console.log('User id:', userId);
            const res = await collabApi.reconnect();
            console.log('Reconnect response:', res);
            if (res.error) console.warn('Reconnect API failed:', res.error);
            setIsReconnecting(false);
          } else {
            toast.success('Connected to collaboration room');
          }

          const res = await collabApi.connect(matchDetails);
          if (res.data && res.data?.message) {
            try {
              console.log('Problem data:', res.data.message);
              const question = res.data.message.question;
              const partner = res.data.message.partner_name;
              setProblem(question);
              setPartnerName(partner);
            } catch {
              console.warn('Invalid problem JSON');
            }
          }
          if (res.error) console.warn('Connect API failed:', res.error);

          startHeartbeat();
        };

        ws.onmessage = (e) => {
          const data = JSON.parse(e.data);
          console.log('Message:', data);

          if (data.message === 'partner_left') {
            toast.error('Your partner left the session');
          } else if (data.message === 'match_terminate') {
            // Partner terminated the session, force exit
            toast.info('Your partner ended the session. Exiting session...');
            localStorage.removeItem('collab_code');
            setTimeout(() => {
              navigate('/matching');
            }, 2000);
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
      const code = localStorage.getItem('collab_code') || '';
      const res = await collabApi.terminate(matchDetails, code);

      if (res.error) {
        console.error('Terminate failed:', res.error);
        toast.error('Error exiting session');
        return;
      }
      localStorage.removeItem('collab_code');
      toast.success('Session ended');
      navigate('/matching');
    } catch {
      toast.error('Error exiting session');
    }
  };

  return (
    <CollabProvider roomId={matchDetails}>
      <CollabSession
        userId={userId}
        problem={problem}
        partnerName={partnerName}
        isReconnecting={isReconnecting}
        handleExit={handleExit}
        minutes={minutes}
        seconds={seconds}
      />
      <ToastContainer />
    </CollabProvider>
  );
}
