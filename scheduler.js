const { PythonShell } = require("python-shell");
const schedule = require("node-schedule");

console.log("Starting app.js");

const options = {
  pythonOptions: ["-u"], // get print results in real-time
};

function runPythonScript() {
  PythonShell.run("newFetch.py", options, function (err, results) {
    if (err) throw err;
    // results is an array consisting of messages collected during execution
    console.log("Results:", results);
  });
}

// Schedule the script to run at 00:01 GMT
const job = schedule.scheduleJob({ hour: 0, minute: 1, tz: "Etc/GMT" }, () => {
  console.log("Running Python script at:", new Date());
  runPythonScript();
});
