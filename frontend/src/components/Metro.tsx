import { useState, useEffect } from "react";
import { FieldValues, SubmitHandler, useForm } from "react-hook-form";
import hydmetrologo from "../assets/hydmetrologo.jpg";
import hydroutemap from "../assets/hydmetroroutemap.jpg";
import "./Metro.css";

function Metro() {
    const {
        register,
        handleSubmit,
        formState: { errors }
    } = useForm();

    const [message, setMessage] = useState<string[] | null>(null);
    const [isVisible, setIsVisible] = useState<boolean>(false);
    const [intermediateStations, setIntermediateStations] = useState<string[]>([]);
    const [elements, setElements] = useState<{
        BlueLine: string[];
        RedLine: string[];
        GreenLine: string[];
    }>({
        BlueLine: [],
        RedLine: [],
        GreenLine: []
    });

    useEffect(() => {
        async function fetchData() {
            try {
                const response = await fetch("http://127.0.0.1:5000/get_elements");
                if (response.ok) {
                    const data = await response.json();
                    console.log("Data:", data);
                    setElements({
                        BlueLine: data.elements.BlueLine || [],
                        RedLine: data.elements.RedLine || [],
                        GreenLine: data.elements.GreenLine || []
                    });
                } else {
                    console.error("Failed to fetch elements");
                }
            } catch (error) {
                console.error("Error fetching elements:", error);
            }
        }
        fetchData();
    }, []);

    const toggleVisibility = () => {
        setIsVisible(!isVisible);
    };

    const onSubmit: SubmitHandler<FieldValues> = async (data: FieldValues) => {
        try {
            const response = await fetch("http://127.0.0.1:5000/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    source_station: data.sourceStation,
                    destination_station: data.destinationStation
                })
            });

            if (response.ok) {
                const result = await response.json();
                if ("res" in result) {
                    console.log(result);
                    setMessage([
                        `Distance: ${result.res.distance}`,
                        `Time: ${result.res.time}`,
                        `Cost: ${result.res.cost}`
                    ]);
                    setIntermediateStations(result.res.intermediate_stations || []);
                } else {
                    setMessage([`Error : ${result.error}`]);
                    setIntermediateStations([]);
                }
            } else {
                const error = await response.json();
                setMessage([`Error: ${error.error}`]);
                setIntermediateStations([]);
            }
        } catch (error) {
            setMessage([`Error: ${(error as any).message}`]);
        }
    };

    const renderOptions = (line: "BlueLine" | "RedLine" | "GreenLine") => {
        return elements[line].map((element, index) => (
            <option key={index} value={element}>
                {element}
            </option>
        ));
    };

    return (
        <div className="container mt-4">
            <h1 className="text-dark display-3 mb-5">
                <img
                    src={hydmetrologo}
                    alt="hyderabad metro logo"
                    width="60"
                    className="mx-3 mb-2"
                />
                <u>
                    <b>Metro Journey Planner</b>
                </u>
            </h1>
            <div className="row mt-5 ml-5">
                <div className="col-sm-5">
                    <h1 className="text-warning display-5">Input</h1>
                    <form
                        noValidate
                        className="form text-start w-75 mt-4"
                        onSubmit={handleSubmit(onSubmit)}
                    >
                        <label
                            htmlFor="order"
                            className="form-label text-light fs-4"
                        >
                            Source Station:
                        </label>
                        <select
                            className="form-select form-control mt-2"
                            defaultValue=""
                            {...register("sourceStation", { required: true })}
                        >
                            <option className="text-center" value="" disabled>
                                --------------------Select--------------------
                            </option>
                            <optgroup label="---------------Blue Line---------------">
                                {renderOptions("BlueLine")}
                            </optgroup>
                            <optgroup label="---------------Red Line---------------">
                                {renderOptions("RedLine")}
                            </optgroup>
                            <optgroup label="---------------Green Line---------------">
                                {renderOptions("GreenLine")}
                            </optgroup>
                        </select>
                        {errors.sourceStation?.type === "required" && (
                            <p className="text-danger mt-1 fs-6">
                                *Source Station is required
                            </p>
                        )}
                        <label
                            htmlFor="matrix"
                            className="form-label text-light mt-4 fs-4"
                        >
                            Destination Station:
                        </label>
                        <select
                            className="form-select form-control mt-2"
                            defaultValue=""
                            {...register("destinationStation", {
                                required: true
                            })}
                        >
                            <option className="text-center" value="" disabled>
                                --------------------Select--------------------
                            </option>
                            <optgroup label="---------------Blue Line---------------">
                                {renderOptions("BlueLine")}
                            </optgroup>
                            <optgroup label="---------------Red Line---------------">
                                {renderOptions("RedLine")}
                            </optgroup>
                            <optgroup label="---------------Green Line---------------">
                                {renderOptions("GreenLine")}
                            </optgroup>
                        </select>
                        {errors.destinationStation?.type === "required" && (
                            <p className="text-danger mt-1 fs-6">
                                *Destination Station is required
                            </p>
                        )}
                        <button
                            type="submit"
                            className="btn btn-success mt-4 mx-auto"
                        >
                            Calculate
                        </button>
                    </form>
                </div>
                <div className="col-sm-7">
                    <h1 className="text-warning display-5">Output</h1>
                    {message !== null &&
                        message.map((element, index) => (
                            <h1
                                className="text-dark display-6 mt-4"
                                key={index}
                            >
                                {element}
                            </h1>
                        ))}
                    
                    {intermediateStations.length > 0 && (
                        <div className="mt-5">
                            <h2 className="text-warning display-6">Stations in Between:</h2>
                            <div className="mt-3">
                                {intermediateStations.map((station, index) => (
                                    <span key={index} className="badge bg-secondary me-2 mb-2 p-2">
                                        {station}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
            <div>
                <button
                    className="btn mt-3 btn-primary"
                    onClick={toggleVisibility}
                >
                    {isVisible ? "Hide Map" : "Show Map"}
                </button>
                <br />
                {isVisible && (
                    <img
                        className="mt-3 mb-5"
                        src={hydroutemap}
                        width="1000"
                        alt="Hyderabad Metro Map"
                    />
                )}
            </div>
        </div>
    );
}

export default Metro;
