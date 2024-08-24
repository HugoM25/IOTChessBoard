import './index.scss';
import { Tile } from '../../models/board';
import { pieceMap } from "../../constants/pieces";


type BoardProps = {
    fenString: string,
}

function parseFen(fenString: string): Tile[] {
    let tiles: Tile[] = [];
    let rows = fenString.split("/");
    for (let i = 0; i < rows.length; i++) {
        let row = rows[i];
        let rowTiles: Tile[] = [];
        let isLight = i % 2 === 0; // Start with light if the row index is even, dark if odd
        for (let j = 0; j < row.length; j++) {
            let char = row[j];
            if (char === " ") {
                break;
            }
            if (isNaN(parseInt(char))) {
                rowTiles.push({
                    color: isLight ? "light" : "dark",
                    pieceName: char,
                });
                isLight = !isLight; // Switch color for next tile
            } else {
                for (let k = 0; k < parseInt(char); k++) {
                    rowTiles.push({
                        color: isLight ? "light" : "dark",
                        pieceName: "",
                    });
                    isLight = !isLight; // Switch color for next tile
                }
            }
        }
        tiles = tiles.concat(rowTiles);
    }
    return tiles;
}
export default function Board(props: BoardProps) {

    const tiles : Tile[] = parseFen(props.fenString);

    return (
    <div className="board">
        {
            tiles.map((tile, index) => {
                return (
                    <div className={`tile ${tile.color}`} key={index}>
                        {<img src={pieceMap[tile.pieceName]}  />}
                    </div>
                );
            })
        }
    </div>
    );
}