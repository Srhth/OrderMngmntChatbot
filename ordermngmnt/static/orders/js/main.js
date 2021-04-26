$(function() {
  function start_watson() {
    $.ajax({
        type: "POST",
        url: 'authenticate_start_session_watson/',   
        success:  function(response){
              /*alert(response);*/
              generate_message("Hi! I am Watson.O", 'user');
              generate_message(":D","user");
              generate_message("How may I assist you today?", 'user');
           }
    });   
  }
  window.onload = function() {
    start_watson();
  };
  var chatbot_msg="Please try asking me gain";
  var INDEX = 0; 
  $("#chat-submit").click(function(e) {
    e.preventDefault();
    var msg = $("#chat-input").val();  
    if(msg.trim() == ''){
      return false;
    }
    generate_message(msg, 'self');
    var buttons = [
        {
          name: 'Existing User',
          value: 'existing'
        },
        {
          name: 'New User',
          value: 'new'
        }
      ];
    $.ajax({
        type: "POST",
        url: 'connect_watson/',   
        data: { text: msg },   /* Passing the text data */
        success: function (response, textStatus) {
          /*alert(response);*/
          if (response === "Invalid Session"){
            generate_message("Chat session Inactive. Starting a new session.", 'user'); 
            start_watson();
          }else if (response.constructor === Array){
            var arrayLength = response.length;
            for (var i = 0; i < arrayLength; i++) {
              generate_message(response[i], 'user'); 
            }
          }else{
            generate_message(response, 'user'); 
          }
        },
        error: function (xhr, textStatus, errorThrown) {
            generate_message("Error! Sorry. Try refreshing the page", 'user');
            generate_message(errorThrown, "user");
            generate_message(textStatus, "user");
            generate_message("You can also try reframing the Query.", 'user');
        },
        fail: function (xhr, textStatus, errorThrown) {
            /*alert(errorThrown);*/
            generate_message("Failed! Sorry. Try refreshing the page", 'user');
            generate_message("You can also try reframing the Query.", 'user');
        }
    });
    
  })
  
  function generate_message(msg, type) {
    INDEX++;
    var str="";
    str += "<div id='cm-msg-"+INDEX+"' class=\"chat-msg "+type+"\">";
    str += "          <div class=\"cm-msg-text\">";
    str += msg;
    str += "          <\/div>";
    str += "        <\/div>";
    $(".chat-logs").append(str);
    $("#cm-msg-"+INDEX).hide().fadeIn(300);
    if(type == 'self'){
     $("#chat-input").val(''); 
    }    
    $(".chat-logs").stop().animate({ scrollTop: $(".chat-logs")[0].scrollHeight}, 1000);    
  }  
  
  function generate_button_message(msg, buttons){    
    /* Buttons should be object array 
      [
        {
          name: 'Existing User',
          value: 'existing'
        },
        {
          name: 'New User',
          value: 'new'
        }
      ]
    */
    INDEX++;
    var btn_obj = buttons.map(function(button) {
       return  "              <li class=\"button\"><a href=\"javascript:;\" class=\"btn btn-primary chat-btn\" chat-value=\""+button.value+"\">"+button.name+"<\/a><\/li>";
    }).join('');
    var str="";
    str += "<div id='cm-msg-"+INDEX+"' class=\"chat-msg user\">";
    str += "          <span class=\"msg-avatar\">";
    str += "            <img src=\"https:\/\/image.crisp.im\/avatar\/operator\/196af8cc-f6ad-4ef7-afd1-c45d5231387c\/240\/?1483361727745\">";
    str += "          <\/span>";
    str += "          <div class=\"cm-msg-text\">";
    str += msg;
    str += "          <\/div>";
    str += "          <div class=\"cm-msg-button\">";
    str += "            <ul>";   
    str += btn_obj;
    str += "            <\/ul>";
    str += "          <\/div>";
    str += "        <\/div>";
    $(".chat-logs").append(str);
    $("#cm-msg-"+INDEX).hide().fadeIn(300);   
    $(".chat-logs").stop().animate({ scrollTop: $(".chat-logs")[0].scrollHeight}, 1000);
    $("#chat-input").attr("disabled", true);
  }
  
  $(document).delegate(".chat-btn", "click", function() {
    var value = $(this).attr("chat-value");
    var name = $(this).html();
    $("#chat-input").attr("disabled", false);
    generate_message(name, 'self');
  })
  
  $("#chat-circle").click(function() {    
    $("#chat-circle").toggle('scale');
    $(".chat-box").toggle('scale');
  })
  
  $(".chat-box-toggle").click(function() {
    $("#chat-circle").toggle('scale');
    $(".chat-box").toggle('scale');
  })
  

})

