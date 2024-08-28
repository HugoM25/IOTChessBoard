import React from "react";
import './index.scss';

type ClockProps = {
    isWhite: boolean;
    timeInSeconds: number; // Add this prop to accept the time in seconds
}

export default function Clock(props: ClockProps) {
    // Function to convert seconds to HH:MM:SS format
    const formatTime = (seconds: number) => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);

        // Pad the hours, minutes, and seconds with leading zeros if necessary
        const formattedHours = String(hours).padStart(2, '0');
        const formattedMinutes = String(minutes).padStart(2, '0');
        const formattedSeconds = String(secs).padStart(2, '0');

        return `${formattedHours}:${formattedMinutes}:${formattedSeconds}`;
    };

    // Convert the prop value to HH:MM:SS format
    const formattedTime = formatTime(props.timeInSeconds);

    return (
        <div className={`clock ${props.isWhite ? "white" : "black"}`}>
            <span>{formattedTime}</span>
        </div>
    );
}
