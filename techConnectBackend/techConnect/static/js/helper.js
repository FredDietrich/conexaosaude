const form = $('#form');
form.submit(event => {
    event.preventDefault();
    $('.invalid-feedback').remove()
    $('.form-group').removeClass('is-invalid');
    $('.form-control').removeClass('is-invalid')
    const formData = Object.fromEntries(new FormData(event.target));
    console.log(formData)
    const emailTest = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(formData.email)
    const phoneTest = /^\d{11}$/.test(formData.phone)
    const passwordTest = /^.*(?=.{6,})(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*? ]).*$/.test(formData.password)
    const cpfTest = /^\d{11}$/.test(formData.cpf)
    if (!emailTest) {
        $('#id_email').addClass('is-invalid');
        $('#id_email').parent().addClass('is-invalid');
        $('<div class="invalid-feedback">Email inválido.</div>').insertAfter('#id_email');
    }
    if (!cpfTest) {
        $('#id_cpf').addClass('is-invalid');
        $('#id_cpf').parent().addClass('is-invalid');
        $('<div class="invalid-feedback">CPF Inválido.</div>').insertAfter('#id_cpf');
    }
    if (!passwordTest) {
        $('#id_password').addClass('is-invalid');
        $('#id_password').parent().addClass('is-invalid');
        $('<div class="invalid-feedback">A senha precisa conter um caractere de letra minúscula, um de letra maiúscula, um número, um caractere especial (!@#$%^&?) e ter ao menos 6 caracteres.</div>').insertAfter('#id_password');
    }
    if (!phoneTest) {
        $('#id_phone').addClass('is-invalid');
        $('#id_phone').parent().addClass('is-invalid');
        $('<div class="invalid-feedback">Telefone inválido.</div>').insertAfter('#id_phone');
    }
    if (emailTest && cpfTest && passwordTest && phoneTest) {
        event.currentTarget.submit();
    } else {
        return;
    }
}) 