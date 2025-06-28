import { useState, useCallback, useRef } from 'react';

interface UseVoiceRecorderReturn {
    isRecording: boolean;
    isPaused: boolean;
    recordingTime: number;
    startRecording: () => Promise<void>;
    stopRecording: () => void;
    pauseRecording: () => void;
    resumeRecording: () => void;
    resetRecording: () => void;
    audioBlob: Blob | null;
    error: string | null;
}

export const useVoiceRecorder = (): UseVoiceRecorderReturn => {
    const [isRecording, setIsRecording] = useState(false);
    const [isPaused, setIsPaused] = useState(false);
    const [recordingTime, setRecordingTime] = useState(0);
    const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
    const [error, setError] = useState<string | null>(null);

    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const timerRef = useRef<NodeJS.Timeout | null>(null);
    const chunksRef = useRef<Blob[]>([]);

    const startTimer = useCallback(() => {
        timerRef.current = setInterval(() => {
            setRecordingTime((prev) => prev + 1);
        }, 1000);
    }, []);

    const stopTimer = useCallback(() => {
        if (timerRef.current) {
            clearInterval(timerRef.current);
            timerRef.current = null;
        }
    }, []);

    const startRecording = useCallback(async () => {
        try {
            setError(null);
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            streamRef.current = stream;

            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus',
            });

            mediaRecorderRef.current = mediaRecorder;
            chunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    chunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {
                const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
                setAudioBlob(blob);
                setIsRecording(false);
                setIsPaused(false);
                stopTimer();
            };

            mediaRecorder.onpause = () => {
                setIsPaused(true);
                stopTimer();
            };

            mediaRecorder.onresume = () => {
                setIsPaused(false);
                startTimer();
            };

            mediaRecorder.start();
            setIsRecording(true);
            setRecordingTime(0);
            startTimer();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to start recording');
            console.error('Error starting recording:', err);
        }
    }, [startTimer, stopTimer]);

    const stopRecording = useCallback(() => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            if (streamRef.current) {
                streamRef.current.getTracks().forEach((track) => track.stop());
                streamRef.current = null;
            }
        }
    }, [isRecording]);

    const pauseRecording = useCallback(() => {
        if (mediaRecorderRef.current && isRecording && !isPaused) {
            mediaRecorderRef.current.pause();
        }
    }, [isRecording, isPaused]);

    const resumeRecording = useCallback(() => {
        if (mediaRecorderRef.current && isRecording && isPaused) {
            mediaRecorderRef.current.resume();
        }
    }, [isRecording, isPaused]);

    const resetRecording = useCallback(() => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
        }
        if (streamRef.current) {
            streamRef.current.getTracks().forEach((track) => track.stop());
            streamRef.current = null;
        }
        setIsRecording(false);
        setIsPaused(false);
        setRecordingTime(0);
        setAudioBlob(null);
        setError(null);
        stopTimer();
    }, [isRecording, stopTimer]);

    return {
        isRecording,
        isPaused,
        recordingTime,
        startRecording,
        stopRecording,
        pauseRecording,
        resumeRecording,
        resetRecording,
        audioBlob,
        error,
    };
}; 