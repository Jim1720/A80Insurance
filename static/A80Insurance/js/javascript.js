
/* javascript.cs */

 

/* historyposition.js */

/* process relocations based on buttons at end of each claim shown */ 

/* ref:
https://stackoverflow.com/questions/72236976/rails-7-jquery-uncaught-referenceerror-is-not-defined
*/



function positionTo(value) {
      

    // go to top, bot, middle or to claim id number in value clause
    if (value == "top") {
        $(document).scrollTop($("#top").offset().top);
    }
    if (value == "mid") {
        $(document).scrollTop($("#mid").offset().top);
    }
    if (value == "bot") {
        $(document).scrollTop($("#bot").offset().top);
    }

    arr = value.split(",");
    claimNumber = arr[1];
    
    // position to claim number
    $(window).scrollTop($("*:contains('" + claimNumber + "'):last").offset().top); 

}; 

function positionToAct1() {

    elementId = document.getElementById("act1");
    value = elementId.value;
    positionTo(value);

};

function positionToAct2() { 
    
    elementId = document.getElementById("act2");
    value = elementId.value;
    positionTo(value);

};