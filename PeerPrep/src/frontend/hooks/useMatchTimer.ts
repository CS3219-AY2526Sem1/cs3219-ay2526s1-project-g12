import { useEffect, useRef, useState } from "react";

export function useMatchTimer(
    active: boolean,
    initialTime = 180,
    onTimeout?: () => void
) {
    const [timeLeft, setTimeLeft] = useState(initialTime);
    const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

    useEffect(() => {
        if (active && timeLeft > 0) {
            timerRef.current = setInterval(() => {
                setTimeLeft((prev) => prev - 1);
            }, 1000);
        }
        return () => {
            if (timerRef.current) clearInterval(timerRef.current);
        };
    }, [active]);

    useEffect(() => {
        if (active && timeLeft === 0 && onTimeout) onTimeout();
    }, [timeLeft]);

    const reset = (seconds = initialTime) => setTimeLeft(seconds);
    const stop = () => {
        if (timerRef.current) clearInterval(timerRef.current);
    };
    const addTime = (seconds: number) => setTimeLeft((prev) => prev + seconds);

    const minutes = Math.floor(timeLeft / 60)
        .toString()
        .padStart(2, "0");
    const seconds = (timeLeft % 60).toString().padStart(2, "0");

    return { timeLeft, minutes, seconds, reset, addTime, stop };
}
