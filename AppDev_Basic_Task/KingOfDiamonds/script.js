const userInput = document.getElementById("userNumber")
const playBtn = document.getElementById("playBtn")
const results = document.getElementById("results")

playBtn.addEventListener("click", function(){
    const userNumber = Number(userInput.value)
    if(userInput.value === ""){
        results.innerHTML = "<p>Please enter a number.</p>"
    return
    } else if (userNumber < 0 || userNumber > 100){
    results.innerHTML = "<p>Enter a number between 0 and 100.</p>"
    return
    } else if (!Number.isInteger(userNumber)){
    results.innerHTML ="<p>Enter a whole number.</p>"
    return
    }
    const botNumber = Math.floor(Math.random() * 101)
    console.log(botNumber)
    const average = (userNumber + botNumber)/2
    const target = average * 0.8
    console.log(target.toFixed(2))
    const userDistance = Math.abs(userNumber - target)
    const botDistance = Math.abs(botNumber - target)
    let winner = ""
    if (userDistance < botDistance){
        winner = "User"
    } else if (botDistance < userDistance){
        winner = "Bot"
    } else {
        winner = "Tie"
    }
    results.innerHTML =
`
<p>User Number: ${userNumber}</p>

<p>Bot Number: ${botNumber}</p>

<p>Average: ${average.toFixed(2)}</p>

<p>Target: ${target.toFixed(2)}</p>

<p><strong>Winner: ${winner}</strong></p>
`
})

