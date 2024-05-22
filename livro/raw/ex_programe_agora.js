function initGlobals() {
  // use "pyodide.runPython(`...`);" to run Python code
}


function handleExercises() {
  const lastTermValue = termEchoLog[termEchoLog.length - 1];
  if (lastTermValue === '103') {
    $("#exCalc").addClass('exercise-correct');
  }
  const lastTermValueLower = lastTermValue.toLowerCase().replace(",", "");
  if (lastTermValue === 'Olá, mundo!' || lastTermValueLower.includes("ola mundo")) {
    $("#exMundo").addClass('exercise-correct');
  }
}
