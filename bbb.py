import streamlit as st
import streamlit.components.v1 as components

form = st.form("my_form")
form.text_input("Tell me your secrets", key="text")
form.form_submit_button("Submit")

st.write("if enter pressed")
st.write(st.session_state["text"])

components.html(
    """
<script>
const doc = window.parent.document;
buttons = Array.from(doc.querySelectorAll('button[kind=secondaryFormSubmit]'));
const submit = buttons.find(el => el.innerText === 'Submit');

doc.addEventListener('keydown', function(e) {
    switch (e.keyCode) {
        case 13: // (37 = enter)
            submit.click();
    }
});
</script>
""",
    height=0,
    width=0,
)