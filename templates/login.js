$(function(){
    var loginHost = '/api/user/action/';
    var cookie_namespace = 'nicar15lightningtalks-';
    var fingerprint = new Fingerprint({canvas: true}).get();

    var $loggedIn = $('#logged-in');
    var $loggedOut = $('#logged-out');
    var $userId = $('#user-id');
    var $submitLogin = $('#submit-login');
    var $submitLogout = $('#submit-logout');
    var $password = $('#password-login');
    var $email = $('#email-login');

    var set_login_status = function(logged_in, user) {
        console.log(logged_in, user);
        if (logged_in) {
            $userId.html(user);
            $loggedOut.hide();
            $loggedIn.show();
        } else {
            $loggedIn.hide();
            $loggedOut.show();
        }
    }

    var check_cookie = function() {
        if ($.cookie(cookie_namespace + 'user') !== undefined){
            set_login_status(true, $.cookie(cookie_namespace + 'user'));
        } else {
            set_login_status(false, null);
        }
    }

    var user_login = function() {
        var user = {};
        user['email'] = $email.val();
        user['password'] = $password.val();
        user['fingerprint'] = fingerprint;
        $.ajax(loginHost + '?email=' + $email.val() + '&password=' + $password.val() + '&fingerprint=' + fingerprint, {
            async: true,
            cache: false,
            crossDomain: false,
            dataType: 'json',
            jsonp: false,
            success: function(data) {
                console.log(data);
                if (data['success'] === true) {
                    $.cookie(cookie_namespace + 'user', data['_id']);
                    set_login_status(true, data['_id']);
                } else {
                    console.log('failed');
                }
            }
        });
    }

    var user_logout = function() {
        $.removeCookie(cookie_namespace + 'user');
        set_login_status(false, null);
    }

    $submitLogin.on('click', user_login);
    $submitLogout.on('click', user_logout);
    check_cookie();
});