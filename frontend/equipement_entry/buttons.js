//create button

var myStartButton = document.createElement("a");

myStartButton.id = "button-9999999-btnInnerEl";

//Add classes

myStartButton.classList.add("x-btn");

myStartButton.classList.add("x-unselectable");

myStartButton.classList.add("uft-id-createcase");

myStartButton.classList.add("x-btn-default-small");

myStartButton.classList.add("x-btn-inner-default-small");

myStartButton.innerHTML = "START " + iEAMdevToolVersion;

//Höche und Breite des Buttons

myStartButton.style.width = '280px';

myStartButton.style.height = '60px';

//Postion des Buttons

myStartButton.style.left = "150px" //vLastElePos.bottom + "px";

//myStartButton.style.right = "500px" //vLastElePos.bottom + "px";

//myStartButton.style.position = "fixed";

//Button font

myStartButton.style.textAlign = "center";

myStartButton.style.fontSize = "30px";

myStartButton.style.margin = "auto";

//Button style

myStartButton.style.border = "8px solid green";

//document.getElementById("button-9999999-btnInnerEl").style.borderColor = "lightblue";

//myStartButton.style.borderColor = 'red';

myStartButton.style.padding = "15px"; //Position in the Button

//Click Event hinzufügen

myStartButton.addEventListener("click", StartSession);

//add button to form

var idField = document.getElementsByClassName("x-autocontainer-innerCt")[gvContainerNummer]; //

idField.appendChild(myStartButton);

function StartSession() {

    if (gvThisForm._record.data.wspf_10_devm_seq) {

        //load existing session

        OpenEAMDevToolWindow();

    } else {

        EAM.Messaging.showError('Please select an existing session or create a new.');

    };

}; //end StartSession
