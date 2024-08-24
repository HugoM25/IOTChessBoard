import "./index.scss"
import { useState } from 'react'

export default function BoardPage() {

    const [brightness, setBrightness] = useState(50);
    const [underAttackColor, setUnderAttackColor] = useState("#ff0000");
    const [availableMovesColor, setAvailableMovesColor] = useState("#00ff00");
    const [ForcedMovesColor, setForcedMovesColor] = useState("#0000ff");

    const ResetSettings = () => {
        setBrightness(50);
        setUnderAttackColor("#ff0000");
        setAvailableMovesColor("#00ff00");
        setForcedMovesColor("#0000ff");
    };

    const handleBrightnessChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = Number(e.target.value);
        setBrightness(value);
        e.target.style.backgroundSize = `${value}% 100%`;
    };

    return (
        <>
        <div className="settings-page">
            <h1>Settings</h1>
            <hr></hr>
            <div className="led-settings">
                <h2>LEDs Options</h2>
                <div className="brightness-selection-led">
                    <label>LEDs Brightness</label>
                    <input 
                        type="range" 
                        min="0" 
                        max="100" 
                        value={brightness} 
                        onInput={handleBrightnessChange} 
                        style={{ backgroundSize: `${brightness}% 100%` }}
                    />               
                </div>
                <div className="color-selection-led">
                    <div>
                        <label>Under attack piece color</label>
                        <input 
                            type="color" 
                            value={underAttackColor} 
                            onChange={(e) => setUnderAttackColor(e.target.value)} 
                        />
                    </div>
                    <div>
                        <label>Available moves color</label>
                        <input 
                            type="color" 
                            value={availableMovesColor} 
                            onChange={(e) => setAvailableMovesColor(e.target.value)} 
                        />
                    </div>
                    <div>
                        <label>Forced moves color</label>
                    <input 
                            type="color" 
                            value={ForcedMovesColor} 
                            onChange={(e) => setForcedMovesColor(e.target.value)} 
                        />
                    </div>

                </div>
            </div>
            <div className="reset-settings">
                <label>Factory RESET?</label>
                <button onClick={ResetSettings} >Reset</button>
            </div>
        </div>
        </>
    );
}