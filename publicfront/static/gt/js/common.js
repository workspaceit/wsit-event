var base_url = window.location.origin + '/gt';

function validateEmail(email) {
    //var re = /^([\w-]+(?:\.[\w-]+)*)@(\bse.gt|\bworkspaceit|\bgmail|\bspringconf).([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
    var re = /^([\w-]+(?:\.[\w-]+)*)@(\bworkspaceit|\bspringconf|\bse.gt).(\bcom)$/;
    return re.test(email);
}
