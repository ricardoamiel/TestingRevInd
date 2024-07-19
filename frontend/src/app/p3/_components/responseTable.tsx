import React from "react";

export interface ResponseTableP3Props {
  responseData: {
    results: [
      {
        id: number;
        score: number;
      }
    ];
    time: number;
  };
  usableData: boolean;
}

function ResponseTableP3({ responseData, usableData }: ResponseTableP3Props) {
  if (!usableData) {
    return <></>;
  }
  const handleDownload = () => {
    const trackId = (document.getElementById("trackIdField") as HTMLInputElement)
      .value;
    if (!trackId) {
      alert("Please fill in all fields");
      return;
    }
    window.open(`http://localhost:5000/download/${trackId}`);
  };
  return (
    <div className="mt-6">
      <div className="flex justify-evenly">
        <div className="bg-white bg-opacity-10 p-10 rounded-md my-3 w-[35vw]">
          <h2 className="text-2xl">Resultados de búsqueda (In-Memory)</h2>
          <div className="overflow-hidden rounded-lg mt-4">
            <table className="w-full text-center">
              <thead>
                <tr className="bg-slate-400 bg-opacity-10">
                  <th>Track ID</th>
                  <th>Score</th>
                </tr>
              </thead>
              <tbody>
                {responseData?.results.map((result: any, index: number) => (
                  <tr
                    key={index}
                    className=" even:bg-slate-400 odd:bg-slate-800 even:bg-opacity-10 odd-bg-opacity:10"
                  >
                    <td>{result.id}</td>
                    <td>{result.score.toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="flex flex-col justify-evenly align-middle">
          <div className="bg-white bg-opacity-10 p-10 rounded-md my-3 text-center">
            Tiempo de búsqueda (In-Memory): {responseData?.time.toFixed(4)}
            ms
          </div>
          <div className="bg-white w-[100%] bg-opacity-10 p-4 rounded-md flex justify-between items-center px-10">
            <input
              type="number"
              id="trackIdField"
              placeholder="Track ID"
              className="p-2 my-4 rounded-md grow mr-2"
            />
            <button
              className="bg-blue-600 p-2 rounded-md text-white hover:bg-blue-800"
              onClick={handleDownload}
            >
              Download
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResponseTableP3;
