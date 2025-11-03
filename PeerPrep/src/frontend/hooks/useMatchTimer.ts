import { useEffect, useRef, useState } from 'react';

export function useMatchTimer(
    active: boolean,
    initialTime = 180,
    onTimeout?: () => void,
    countDown = true,
) {
  const [timeLeft, setTimeLeft] = useState(initialTime);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

    useEffect(() => {
        if (active) {
            timerRef.current = setInterval(() => {
                setTimeLeft((prev) => (countDown ? (timeLeft > 0 ? prev - 1 : 0) : prev + 1));
            }, 1000);
        }
        return () => {
            if (timerRef.current) clearInterval(timerRef.current);
        };
    }, [active]);

    useEffect(() => {
        if (countDown && active && timeLeft === 0 && onTimeout) onTimeout();
    }, [timeLeft, countDown]);

  const reset = (seconds = initialTime) => setTimeLeft(seconds);
  const stop = () => {
    if (timerRef.current) clearInterval(timerRef.current);
  };
  const addTime = (seconds: number) => setTimeLeft((prev) => prev + seconds);

  const minutes = Math.floor(timeLeft / 60)
    .toString()
    .padStart(2, '0');
  const seconds = (timeLeft % 60).toString().padStart(2, '0');

  return { timeLeft, minutes, seconds, reset, addTime, stop };
}
