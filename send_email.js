// Usage:
// node send_email.js SERVICE_ID TEMPLATE_ID RECIPIENT_EMAIL TEMPLATE_VARS_JSON PUBLIC_KEY PRIVATE_KEY
// Example:
// node send_email.js service_xxx template_xxx "user@email.com" '{"name":"James","notes":"Check this out!"}' public_xxx private_xxx

import emailjs from '@emailjs/nodejs';

async function main() {
  const [
    ,,
    serviceId,
    templateId,
    publicKey,
    templateVarsJson,
  ] = process.argv;

  if (!serviceId || !templateId || !publicKey || !templateVarsJson) {
    console.error('Usage: node send_email.js SERVICE_ID TEMPLATE_ID PUBLIC_KEY TEMPLATE_VARS_JSON');
    process.exit(1);
  }

  let templateParams;
  try {
    templateParams = JSON.parse(templateVarsJson);
  } catch (e) {
    console.error('Invalid TEMPLATE_VARS_JSON:', e.message);
    process.exit(1);
  }

  try {
    const response = await emailjs.send(
      serviceId,
      templateId,
      templateParams,
      {
        publicKey: publicKey
      }
    );
    console.log('SUCCESS', response.status, response.text);
    process.exit(0);
  } catch (err) {
    console.error('FAILED', err && err.text ? err.text : err);
    process.exit(2);
  }
}

main();
