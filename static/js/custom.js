function buyAll() {
    buy = document.getElementById("buyallButton");
    
    buy.addEventListener("click", checkOut);
}

function checkOut(event){ 
    buybutton = event.target
    
    customer_id = buybutton.dataset.customer;
    console.log("called")
    urlForCheckout = "/checking_out/" + customer_id;
    fetch(urlForCheckout).then(
        response => {
            if (response.status == 200){show();}
            else{response.json().then(data => show2(data["error"]));}
        }
    ).catch(
        err => console.log("error happened")
    )
}

function show(){
    mess = document.getElementById("modalMessage")
    mess.innerHTML = "Thank you for buying from us!";
    
}
function show2(d){
    mess = document.getElementById("modalMessage")
    mess.innerHTML = d;
    
}