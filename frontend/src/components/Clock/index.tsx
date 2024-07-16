import React, { useEffect } from "react";
import './index.scss';


type ClockProps = {
    isWhite: boolean;
}

export default function Clock(props: ClockProps) {

    const [time, setTime] = React.useState('00:00:00');

    return (
        <div className={`clock ${props.isWhite ? "white" : "black"}`}>
            <span>{time}</span>
        </div>
    );
}