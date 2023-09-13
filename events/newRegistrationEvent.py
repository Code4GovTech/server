import smtplib
from email.message import EmailMessage

def generateMappingTemplate(org, email, mappings):
    mappingRows = ''
    for mapping in mappings:
        mappingRows+=f'''<tr>
                            <td style="font-size: 15px; color: #000000; padding: 10px 5px 10px 10px; width: 50%;">{mapping["name"]}</td>
                            <td style="border: 2px solid #d9d9d9; font-size: 15px; color: #000000; padding: 10px 5px 10px 5px; width: 50%;text-align: center; vertical-align: middle;">{mapping["product"]}</td>
                            <td style="padding: 10px;"></td>
                          </tr>'''
    registrationMappingEmail = f'''<!doctype html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">

<head>
  <title>
  </title>
  <!--[if !mso]><!-->
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <!--<![endif]-->
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style type="text/css">
    #outlook a {{
      padding: 0;
    }}

    body {{
      margin: 0;
      padding: 0;
      -webkit-text-size-adjust: 100%;
      -ms-text-size-adjust: 100%;
    }}

    table,
    td {{
      border-collapse: collapse;
      mso-table-lspace: 0pt;
      mso-table-rspace: 0pt;
    }}

    img {{
      border: 0;
      height: auto;
      line-height: 100%;
      outline: none;
      text-decoration: none;
      -ms-interpolation-mode: bicubic;
    }}

    p {{
      display: block;
      margin: 13px 0;
    }}
  </style>
  <!--[if mso]>
        <noscript>
        <xml>
        <o:OfficeDocumentSettings>
          <o:AllowPNG/>
          <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
        </xml>
        </noscript>
        <![endif]-->
  <!--[if lte mso 11]>
        <style type="text/css">
          .mj-outlook-group-fix {{ width:100% !important; }}
        </style>
        <![endif]-->
  <!--[if !mso]><!-->
  <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700" rel="stylesheet" type="text/css">
  <link href="https://fonts.googleapis.com/css?family=Ubuntu:300,400,500,700" rel="stylesheet" type="text/css">
  <style type="text/css">
    @import url(https://fonts.googleapis.com/css?family=Roboto:300,400,500,700);
    @import url(https://fonts.googleapis.com/css?family=Ubuntu:300,400,500,700);
  </style>
  <!--<![endif]-->
  <style type="text/css">
    @media only screen and (min-width:480px) {{
      .mj-column-per-80 {{
        width: 80% !important;
        max-width: 80%;
      }}

      .mj-column-per-20 {{
        width: 20% !important;
        max-width: 20%;
      }}

      .mj-column-per-100 {{
        width: 100% !important;
        max-width: 100%;
      }}

      .mj-column-per-30 {{
        width: 30% !important;
        max-width: 30%;
      }}

      .mj-column-per-9 {{
        width: 9% !important;
        max-width: 9%;
      }}

      .mj-column-per-8 {{
        width: 8% !important;
        max-width: 8%;
      }}

      .mj-column-per-10 {{
        width: 10% !important;
        max-width: 10%;
      }}
    }}
  </style>
  <style media="screen and (min-width:480px)">
    .moz-text-html .mj-column-per-80 {{
      width: 80% !important;
      max-width: 80%;
    }}

    .moz-text-html .mj-column-per-20 {{
      width: 20% !important;
      max-width: 20%;
    }}

    .moz-text-html .mj-column-per-100 {{
      width: 100% !important;
      max-width: 100%;
    }}

    .moz-text-html .mj-column-per-30 {{
      width: 30% !important;
      max-width: 30%;
    }}

    .moz-text-html .mj-column-per-9 {{
      width: 9% !important;
      max-width: 9%;
    }}

    .moz-text-html .mj-column-per-8 {{
      width: 8% !important;
      max-width: 8%;
    }}

    .moz-text-html .mj-column-per-10 {{
      width: 10% !important;
      max-width: 10%;
    }}
  </style>
  <style type="text/css">
    @media only screen and (max-width:480px) {{
      table.mj-full-width-mobile {{
        width: 100% !important;
      }}

      td.mj-full-width-mobile {{
        width: auto !important;
      }}
    }}
  </style>
</head>

<body style="word-spacing:normal;background-color:#ffffff;">
  <div style="background-color:#ffffff;">
    <!-- Header Section -->
    <!--[if mso | IE]><table align="center" border="0" cellpadding="0" cellspacing="0" class="" style="width:600px;" width="600" bgcolor="#fdf7db" ><tr><td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
    <div style="background:#fdf7db;background-color:#fdf7db;margin:0px auto;max-width:600px;">
      <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="background:#fdf7db;background-color:#fdf7db;width:100%;">
        <tbody>
          <tr>
            <td style="direction:ltr;font-size:0px;padding:5px 0px 5px 0px;text-align:center;">
              <!--[if mso | IE]><table role="presentation" border="0" cellpadding="0" cellspacing="0"><tr><td class="" style="vertical-align:middle;width:480px;" ><![endif]-->
              <div class="mj-column-per-80 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:middle;width:100%;">
                <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:middle;" width="100%">
                  <tbody>
                    <!-- Main title -->
                    <tr>
                      <td align="center" style="font-size:0px;padding:0px;word-break:break-word;">
                        <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen-Sans,Ubuntu,Cantarell,'Helvetica Neue',sans-serif;;font-size:23.5px;font-weight:bold;line-height:24px;text-align:center;color:#294294;">CODE FOR GOVTECH</div>
                      </td>
                    </tr>
                    <!-- Subtitle -->
                    <tr>
                      <td align="center" style="font-size:0px;padding:0px;word-break:break-word;">
                        <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen-Sans,Ubuntu,Cantarell,'Helvetica Neue',sans-serif;;font-size:15px;font-weight:400;line-height:24px;text-align:center;color:#cd3c60;">Building Digital Public Goods</div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <!--[if mso | IE]></td><![endif]-->
              <!-- Logo - right aligned -->
              <!--[if mso | IE]><td class="" style="vertical-align:middle;width:120px;" ><![endif]-->
              <div class="mj-column-per-20 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:middle;width:100%;">
                <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:middle;" width="100%">
                  <tbody>
                    <tr>
                      <td align="right" style="font-size:0px;padding:0px;word-break:break-word;">
                        <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;">
                          <tbody>
                            <tr>
                              <td style="width:120px;">
                                <img alt="Elaborate Logo" height="auto" src="https://raw.githubusercontent.com/KDwevedi/c4gt-docs/main/assets/C4GT%20India%20Logo.png" style="border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;" width="120" />
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <!--[if mso | IE]></td></tr></table><![endif]-->
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <!--[if mso | IE]></td></tr></table><table align="center" border="0" cellpadding="0" cellspacing="0" class="" style="width:600px;" width="600" ><tr><td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
    <div style="margin:0px auto;max-width:600px;">
      <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;">
        <tbody>
          <tr>
            <td style="direction:ltr;font-size:0px;padding:20px 0;text-align:center;">
              <!--[if mso | IE]><table role="presentation" border="0" cellpadding="0" cellspacing="0"><tr><td class="" style="vertical-align:top;width:600px;" ><![endif]-->
              <div class="mj-column-per-100 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;">
                <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:top;" width="100%">
                  <tbody>
                    <!-- Opening Paragraph -->
                    <tr>
                      <td align="left" style="font-size:0px;padding:0 0 20px 0;word-break:break-word;">
                        <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen-Sans,Ubuntu,Cantarell,'Helvetica Neue',sans-serif;;font-size:15px;font-weight:400;line-height:24px;text-align:left;color:#000000;">Hi, <br><br> Congratulations, you have successfully registered your GitHub organisation and completed the product repository mapping. Your submission is currently under review by the C4GT Team, and you will receive an email confirmation of authentication within a few days. Please find the registered details below:</div>
                      </td>
                    </tr>
                    <!-- Table -->
                    <tr>
                      <td align="left" style="font-size:0px;padding:10px;word-break:break-word;">
                        <table cellpadding="0" cellspacing="0" width="100%" border="0" style="color:#000000;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen-Sans,Ubuntu,Cantarell,'Helvetica Neue',sans-serif;;font-size:13px;line-height:22px;table-layout:auto;width:100%;border:2px solid #d9d9d9;">
                          <!-- Header Row: Organisation Details -->
                          <tr>
                            <td colspan="3" style="font-size: 17px; color: #294294; text-align: left; padding: 10px 10px 10px 10px;">Organisation Details</td>
                          </tr>
                          <!-- Content Rows -->
                          <tr>
                            <td style="font-size: 15px; color: #000000; padding: 10px 5px 10px 10px; width: 50%;">GitHub Organisation</td>
                            <td style="border: 2px solid #d9d9d9; font-size: 15px; color: #000000; padding: 10px 5px 10px 5px; width: 50%; text-align: center; vertical-align: middle;">{org}</td>
                            <td style="padding: 10px;"></td>
                          </tr>
                          <tr>
                            <td style="font-size: 15px; color: #000000; padding: 10px 5px 10px 10px; width: 50%;">Registered Email</td>
                            <td style="border: 2px solid #d9d9d9; font-size: 15px; color: #000000; padding: 10px 5px 10px 5px; width: 50%;text-align: center; vertical-align: middle;">{email}</td>
                            <td style="padding: 10px;"></td>
                          </tr>
                          <!-- Header Row: Product<> Repository Mapping -->
                          <tr>
                            <td colspan="3" style="font-size: 17px; color: #294294; text-align: left; padding: 10px 10px 10px 10px;">Product<> Repository Mapping</td>
                          </tr>
                          <!-- Content Rows -->
                          {mappingRows}
                          <!-- Empty Buffer Row at the bottom -->
                          <tr>
                            <td style="padding: 10px;"></td>
                            <td style="padding: 10px;"></td>
                            <td style="padding: 10px;"></td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                    <!-- Closing Text -->
                    <tr>
                      <td align="left" style="font-size:0px;padding:20px 0;word-break:break-word;">
                        <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen-Sans,Ubuntu,Cantarell,'Helvetica Neue',sans-serif;;font-size:15px;font-weight:400;line-height:24px;text-align:left;color:#000000;">If case, you wish to edit any details, please <a href="http://127.0.0.1:5000/form/edit/{org}">click on this link</a>. You can check out the listed projects on <a href="#">C4GT Community here</a>. <br><br> We look forward to having you onboard with us on C4GT to build an active open-source community for the Digital Public Goods ecosystem in India. <br><br> Warm Regards,<br> C4GT Team</div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <!--[if mso | IE]></td></tr></table><![endif]-->
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <!--[if mso | IE]></td></tr></table><![endif]-->
    <!-- Footer Section -->
    <!--[if mso | IE]><table align="center" border="0" cellpadding="0" cellspacing="0" class="" style="width:600px;" width="600" bgcolor="#ffffff" ><tr><td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
    <div style="background:#ffffff;background-color:#ffffff;margin:0px auto;max-width:600px;">
      <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="background:#ffffff;background-color:#ffffff;width:100%;">
        <tbody>
          <tr>
            <td style="direction:ltr;font-size:0px;padding:20px 0;text-align:center;">
              <!--[if mso | IE]><table role="presentation" border="0" cellpadding="0" cellspacing="0"><tr><td class="" style="width:600px;" ><![endif]-->
              <div class="mj-column-per-100 mj-outlook-group-fix" style="font-size:0;line-height:0;text-align:left;display:inline-block;width:100%;direction:ltr;">
                <!--[if mso | IE]><table border="0" cellpadding="0" cellspacing="0" role="presentation" ><tr><![endif]-->
                <!-- Company Logo - Left aligned -->
                <!--[if mso | IE]><td style="vertical-align:top;width:180px;" ><![endif]-->
                <div class="mj-column-per-30 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:30%;">
                  <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:top;" width="100%">
                    <tbody>
                      <tr>
                        <td align="left" style="font-size:0px;padding:0px;word-break:break-word;">
                          <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;">
                            <tbody>
                              <tr>
                                <td style="width:180px;">
                                  <img alt="Standard Logo" height="auto" src="https://raw.githubusercontent.com/KDwevedi/c4gt-docs/main/assets/C4GT%20Logo.png" style="border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;" width="180" />
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <!--[if mso | IE]></td><![endif]-->
                <!-- Buffer Column -->
                <!--[if mso | IE]><td style="vertical-align:top;width:180px;" ><![endif]-->
                <div class="mj-column-per-30 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:30%;">
                  <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:top;" width="100%">
                    <tbody>
                    </tbody>
                  </table>
                </div>
                <!--[if mso | IE]></td><![endif]-->
                <!-- Social Media Logos - Right aligned -->
                <!--[if mso | IE]><td style="vertical-align:top;width:54px;" ><![endif]-->
                <div class="mj-column-per-9 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:9%;">
                  <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:top;" width="100%">
                    <tbody>
                      <tr>
                        <td align="center" style="font-size:0px;padding:10px 25px;padding-right:5px;padding-left:5px;word-break:break-word;">
                          <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;">
                            <tbody>
                              <tr>
                                <td style="width:44px;">
                                <a href="https://www.linkedin.com/company/code-for-govtech/">
                                  <img alt="LinkedIn" height="auto" src="https://raw.githubusercontent.com/KDwevedi/c4gt-docs/main/assets/LinkedIn%20Logo.png" style="border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;" width="44" />
                                </a>
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <!--[if mso | IE]></td><td style="vertical-align:top;width:48px;" ><![endif]-->
                <div class="mj-column-per-8 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:8%;">
                  <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:top;" width="100%">
                    <tbody>
                      <tr>
                        <td align="center" style="font-size:0px;padding:10px 25px;padding-right:5px;padding-left:5px;word-break:break-word;">
                          <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;">
                            <tbody>
                              <tr>
                                <td style="width:38px;">
                                <a href="https://github.com/Code4GovTech/C4GT/wiki">
                                  <img alt="GitHub" height="auto" src="https://raw.githubusercontent.com/KDwevedi/c4gt-docs/main/assets/Github%20Logo.png" style="border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;" width="38" />
                                </a>
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <!--[if mso | IE]></td><td style="vertical-align:top;width:60px;" ><![endif]-->
                <div class="mj-column-per-10 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:10%;">
                  <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:top;" width="100%">
                    <tbody>
                      <tr>
                        <td align="center" style="font-size:0px;padding:10px 25px;padding-right:5px;padding-left:5px;word-break:break-word;">
                          <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;">
                            <tbody>
                              <tr>
                                <td style="width:50px;">
                                <a href="https://www.youtube.com/channel/UCIi94fH37KkOYieSBZ4Ew4g">
                                  <img alt="YouTube" height="auto" src="https://raw.githubusercontent.com/KDwevedi/c4gt-docs/main/assets/Youtube%20Logo.png" style="border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;" width="50" />
                                </a>
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <!--[if mso | IE]></td><td style="vertical-align:top;width:60px;" ><![endif]-->
                <div class="mj-column-per-10 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:10%;">
                  <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:top;" width="100%">
                    <tbody>
                      <tr>
                        <td align="center" style="font-size:0px;padding:10px 25px;padding-right:5px;padding-left:5px;word-break:break-word;">
                          <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;">
                            <tbody>
                              <tr>
                                <td style="width:50px;">
                                <a href="https://discord.com/invite/QKXpyQDcbg">
                                  <img alt="Discord" height="auto" src="https://raw.githubusercontent.com/KDwevedi/c4gt-docs/main/assets/Discord%20Logo.png" style="border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;" width="50" />
                                </a>
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <!--[if mso | IE]></td></tr></table><![endif]-->
              </div>
              <!--[if mso | IE]></td></tr></table><![endif]-->
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <!--[if mso | IE]></td></tr></table><![endif]-->
  </div>
</body>

</html>'''
    return registrationMappingEmail
registrationAknowledgementEmail = f'''<!doctype html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">

<head>
  <title>
  </title>
  <!--[if !mso]><!-->
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <!--<![endif]-->
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style type="text/css">
    #outlook a {{
      padding: 0;
    }}

    body {{
      margin: 0;
      padding: 0;
      -webkit-text-size-adjust: 100%;
      -ms-text-size-adjust: 100%;
    }}

    table,
    td {{
      border-collapse: collapse;
      mso-table-lspace: 0pt;
      mso-table-rspace: 0pt;
    }}

    img {{
      border: 0;
      height: auto;
      line-height: 100%;
      outline: none;
      text-decoration: none;
      -ms-interpolation-mode: bicubic;
    }}

    p {{
      display: block;
      margin: 13px 0;
    }}
  </style>
  <!--[if mso]>
        <noscript>
        <xml>
        <o:OfficeDocumentSettings>
          <o:AllowPNG/>
          <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
        </xml>
        </noscript>
        <![endif]-->
  <!--[if lte mso 11]>
        <style type="text/css">
          .mj-outlook-group-fix {{ width:100% !important; }}
        </style>
        <![endif]-->
  <!--[if !mso]><!-->
  <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700" rel="stylesheet" type="text/css">
  <link href="https://fonts.googleapis.com/css?family=Ubuntu:300,400,500,700" rel="stylesheet" type="text/css">
  <style type="text/css">
    @import url(https://fonts.googleapis.com/css?family=Roboto:300,400,500,700);
    @import url(https://fonts.googleapis.com/css?family=Ubuntu:300,400,500,700);
  </style>
  <!--<![endif]-->
  <style type="text/css">
    @media only screen and (min-width:480px) {{
      .mj-column-per-80 {{
        width: 80% !important;
        max-width: 80%;
      }}

      .mj-column-per-20 {{
        width: 20% !important;
        max-width: 20%;
      }}

      .mj-column-per-100 {{
        width: 100% !important;
        max-width: 100%;
      }}

      .mj-column-per-30 {{
        width: 30% !important;
        max-width: 30%;
      }}

      .mj-column-per-9 {{
        width: 9% !important;
        max-width: 9%;
      }}

      .mj-column-per-8 {{
        width: 8% !important;
        max-width: 8%;
      }}

      .mj-column-per-10 {{
        width: 10% !important;
        max-width: 10%;
      }}
    }}
  </style>
  <style media="screen and (min-width:480px)">
    .moz-text-html .mj-column-per-80 {{
      width: 80% !important;
      max-width: 80%;
    }}

    .moz-text-html .mj-column-per-20 {{
      width: 20% !important;
      max-width: 20%;
    }}

    .moz-text-html .mj-column-per-100 {{
      width: 100% !important;
      max-width: 100%;
    }}

    .moz-text-html .mj-column-per-30 {{
      width: 30% !important;
      max-width: 30%;
    }}

    .moz-text-html .mj-column-per-9 {{
      width: 9% !important;
      max-width: 9%;
    }}

    .moz-text-html .mj-column-per-8 {{
      width: 8% !important;
      max-width: 8%;
    }}

    .moz-text-html .mj-column-per-10 {{
      width: 10% !important;
      max-width: 10%;
    }}
  </style>
  <style type="text/css">
    @media only screen and (max-width:480px) {{
      table.mj-full-width-mobile {{
        width: 100% !important;
      }}

      td.mj-full-width-mobile {{
        width: auto !important;
      }}
    }}
  </style>
</head>

<body style="word-spacing:normal;background-color:#ffffff;">
  <div style="background-color:#ffffff;">
    <!-- Header Section -->
    <!--[if mso | IE]><table align="center" border="0" cellpadding="0" cellspacing="0" class="" style="width:600px;" width="600" bgcolor="#fdf7db" ><tr><td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
    <div style="background:#fdf7db;background-color:#fdf7db;margin:0px auto;max-width:600px;">
      <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="background:#fdf7db;background-color:#fdf7db;width:100%;">
        <tbody>
          <tr>
            <td style="direction:ltr;font-size:0px;padding:5px 0px 5px 0px;text-align:center;">
              <!--[if mso | IE]><table role="presentation" border="0" cellpadding="0" cellspacing="0"><tr><td class="" style="vertical-align:middle;width:480px;" ><![endif]-->
              <div class="mj-column-per-80 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:middle;width:100%;">
                <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:middle;" width="100%">
                  <tbody>
                    <!-- Main title -->
                    <tr>
                      <td align="center" style="font-size:0px;padding:0px;word-break:break-word;">
                        <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen-Sans,Ubuntu,Cantarell,'Helvetica Neue',sans-serif;;font-size:23.5px;font-weight:bold;line-height:24px;text-align:center;color:#294294;">CODE FOR GOVTECH</div>
                      </td>
                    </tr>
                    <!-- Subtitle -->
                    <tr>
                      <td align="center" style="font-size:0px;padding:0px;word-break:break-word;">
                        <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen-Sans,Ubuntu,Cantarell,'Helvetica Neue',sans-serif;;font-size:15px;font-weight:400;line-height:24px;text-align:center;color:#cd3c60;">Building Digital Public Goods</div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <!--[if mso | IE]></td><![endif]-->
              <!-- Logo - right aligned -->
              <!--[if mso | IE]><td class="" style="vertical-align:middle;width:120px;" ><![endif]-->
              <div class="mj-column-per-20 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:middle;width:100%;">
                <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:middle;" width="100%">
                  <tbody>
                    <tr>
                      <td align="right" style="font-size:0px;padding:0px;word-break:break-word;">
                        <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;">
                          <tbody>
                            <tr>
                              <td style="width:120px;">
                                <img alt="Elaborate Logo" height="auto" src="https://raw.githubusercontent.com/KDwevedi/c4gt-docs/main/assets/C4GT%20India%20Logo.png" style="border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;" width="120" />
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <!--[if mso | IE]></td></tr></table><![endif]-->
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <!--[if mso | IE]></td></tr></table><table align="center" border="0" cellpadding="0" cellspacing="0" class="" style="width:600px;" width="600" ><tr><td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
    <div style="margin:0px auto;max-width:600px;">
      <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;">
        <tbody>
          <tr>
            <td style="direction:ltr;font-size:0px;padding:20px 0;text-align:center;">
              <!--[if mso | IE]><table role="presentation" border="0" cellpadding="0" cellspacing="0"><tr><td class="" style="vertical-align:top;width:600px;" ><![endif]-->
              <div class="mj-column-per-100 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;">
                <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:top;" width="100%">
                  <tbody>
                    <!-- Opening Paragraph -->
                    <tr>
                      <td align="left" style="font-size:0px;padding:0 0 20px 0;word-break:break-word;">
                        <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen-Sans,Ubuntu,Cantarell,'Helvetica Neue',sans-serif;;font-size:15px;font-weight:400;line-height:24px;text-align:left;color:#000000;">Hi, <br><br> We are very excited to inform you that your registration has been authenticated! We look forward to having you on board this mission to build an active open-source coding community in the DPG Ecosystem. <br><br> All tickets listed in the required issue template from the registered repositories will now be listed on the C4GT Community Listing for coders to discover and contribute towards. <br><br> In case you wish to edit any registration details, please <a href="http://127.0.0.1:5000/form/edit/KDwevedi">click this link</a>. Please feel free to reach out to us in case of any queries or concerns at admin@codeforgovtech.in We are very excited about building this community with your support <br><br> Warm Regards, <br> C4GT Team</div>
                      </td>
                    </tr>
                    <!-- Footer Section -->
                    <tr>
                      <td style="font-size:0px;padding:20px 0;word-break:break-word;">
                        <!--[if mso | IE]><table align="center" border="0" cellpadding="0" cellspacing="0" class="" style="width:600px;" width="600" bgcolor="#ffffff" ><tr><td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
                        <div style="background:#ffffff;background-color:#ffffff;margin:0px auto;max-width:600px;">
                          <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="background:#ffffff;background-color:#ffffff;width:100%;">
                            <tbody>
                              <tr>
                                <td style="direction:ltr;font-size:0px;padding:20px 0;text-align:center;">
                                  <!--[if mso | IE]><table role="presentation" border="0" cellpadding="0" cellspacing="0"><tr><td class="" style="width:600px;" ><![endif]-->
                                  <div class="mj-column-per-100 mj-outlook-group-fix" style="font-size:0;line-height:0;text-align:left;display:inline-block;width:100%;direction:ltr;">
                                    <!--[if mso | IE]><table border="0" cellpadding="0" cellspacing="0" role="presentation" ><tr><![endif]-->
                                    <!-- Company Logo - Left aligned -->
                                    <!--[if mso | IE]><td style="vertical-align:top;width:180px;" ><![endif]-->
                                    <div class="mj-column-per-30 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:30%;">
                                      <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:top;" width="100%">
                                        <tbody>
                                          <tr>
                                            <td align="left" style="font-size:0px;padding:0px;word-break:break-word;">
                                              <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;">
                                                <tbody>
                                                  <tr>
                                                    <td style="width:180px;">
                                                      <img alt="Standard Logo" height="auto" src="https://raw.githubusercontent.com/KDwevedi/c4gt-docs/main/assets/C4GT%20Logo.png" style="border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;" width="180" />
                                                    </td>
                                                  </tr>
                                                </tbody>
                                              </table>
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                    </div>
                                    <!--[if mso | IE]></td><![endif]-->
                                    <!-- Buffer Column -->
                                    <!--[if mso | IE]><td style="vertical-align:top;width:180px;" ><![endif]-->
                                    <div class="mj-column-per-30 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:30%;">
                                      <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:top;" width="100%">
                                        <tbody>
                                        </tbody>
                                      </table>
                                    </div>
                                    <!--[if mso | IE]></td><![endif]-->
                                    <!-- Social Media Logos - Right aligned -->
                                    <!--[if mso | IE]><td style="vertical-align:top;width:54px;" ><![endif]-->
                                    <div class="mj-column-per-9 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:9%;">
                                      <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:top;" width="100%">
                                        <tbody>
                                          <tr>
                                            <td align="center" style="font-size:0px;padding:10px 25px;padding-right:5px;padding-left:5px;word-break:break-word;">
                                              <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;">
                                                <tbody>
                                                  <tr>
                                                    <td style="width:44px;">
                                                    <a href="https://www.linkedin.com/company/code-for-govtech/">
                                                      <img alt="LinkedIn" height="auto" src="https://raw.githubusercontent.com/KDwevedi/c4gt-docs/main/assets/LinkedIn%20Logo.png" style="border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;" width="44" />
                                                    </a>
                                                    </td>
                                                  </tr>
                                                </tbody>
                                              </table>
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                    </div>
                                    <!--[if mso | IE]></td><td style="vertical-align:top;width:48px;" ><![endif]-->
                                    <div class="mj-column-per-8 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:8%;">
                                      <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:top;" width="100%">
                                        <tbody>
                                          <tr>
                                            <td align="center" style="font-size:0px;padding:10px 25px;padding-right:5px;padding-left:5px;word-break:break-word;">
                                              <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;">
                                                <tbody>
                                                  <tr>
                                                    <td style="width:38px;">
                                                    <a href="https://github.com/Code4GovTech/C4GT/wiki">
                                                      <img alt="GitHub" height="auto" src="https://raw.githubusercontent.com/KDwevedi/c4gt-docs/main/assets/Github%20Logo.png" style="border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;" width="38" />
                                                    </a>
                                                    </td>
                                                  </tr>
                                                </tbody>
                                              </table>
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                    </div>
                                    <!--[if mso | IE]></td><td style="vertical-align:top;width:60px;" ><![endif]-->
                                    <div class="mj-column-per-10 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:10%;">
                                      <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:top;" width="100%">
                                        <tbody>
                                          <tr>
                                            <td align="center" style="font-size:0px;padding:10px 25px;padding-right:5px;padding-left:5px;word-break:break-word;">
                                              <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;">
                                                <tbody>
                                                  <tr>
                                                    <td style="width:50px;">
                                                    <a href="https://www.youtube.com/channel/UCIi94fH37KkOYieSBZ4Ew4g">
                                                      <img alt="YouTube" height="auto" src="https://raw.githubusercontent.com/KDwevedi/c4gt-docs/main/assets/Youtube%20Logo.png" style="border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;" width="50" />
                                                    </a>
                                                    </td>
                                                  </tr>
                                                </tbody>
                                              </table>
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                    </div>
                                    <!--[if mso | IE]></td><td style="vertical-align:top;width:60px;" ><![endif]-->
                                    <div class="mj-column-per-10 mj-outlook-group-fix" style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:10%;">
                                      <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:top;" width="100%">
                                        <tbody>
                                          <tr>
                                            <td align="center" style="font-size:0px;padding:10px 25px;padding-right:5px;padding-left:5px;word-break:break-word;">
                                              <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;">
                                                <tbody>
                                                  <tr>
                                                    <td style="width:50px;">
                                                    <a href="https://discord.com/invite/QKXpyQDcbg">
                                                      <img alt="Discord" height="auto" src="https://raw.githubusercontent.com/KDwevedi/c4gt-docs/main/assets/Discord%20Logo.png" style="border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;" width="50" />
                                                    </a>
                                                    </td>
                                                  </tr>
                                                </tbody>
                                              </table>
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                    </div>
                                    <!--[if mso | IE]></td></tr></table><![endif]-->
                                  </div>
                                  <!--[if mso | IE]></td></tr></table><![endif]-->
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                        <!--[if mso | IE]></td></tr></table><![endif]-->
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <!--[if mso | IE]></td></tr></table><![endif]-->
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <!--[if mso | IE]></td></tr></table><![endif]-->
  </div>
</body>

</html>'''

def generateHTMLForEmail(organisation,email, repos, auth_link):
    repository_rows = ''
    for repo in repos:
        repository_rows+=f'''<tr>
            <td>{repo["name"]}</td>
            <td>{repo["product"]}</td>
        </tr>'''
    TopHTML = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>C4GT Community Program Onboarding</title>
    <style>
        h2, h4 {{
            text-align: center;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        table, th, td {{
            border: 1px solid black;
        }}
        th, td {{
            padding: 8px;
            text-align: left;
        }}
    </style>
</head>
<body>

<h2>C4GT Community Program</h2>
<h4>Organisation Onboarding</h4>
<br>
<b>Authentication Email</b>
<br>
<p><b>Objective:</b> C4GT Team is able to identify and approve that a valid DPG is being onboarded</p>
<br>
<hr>
<br>
<p>Hi C4GT Team,</p>
<br>
<p>We have received a new registration for the C4GT community program. Please find the details below</p>
<br>
<b>Registration Details</b>
<table>
    <tr>
        <td>Github Organisation's Name</td>
        <td>{organisation}</td>
    </tr>
    <tr>
        <td>PoC Email</td>
        <td>{email}</td>
    </tr>
</table>
<br>
<table>
    <thead>
        <tr>
            <th>Repository Name</th>
            <th>Product Name</th>
        </tr>
    </thead>
    <tbody>
        {repository_rows}
    </tbody>
</table>
<br>
<p>To authenticate this GitHub organisation please click on the link given below. On authentication, the tickets from these repositories will be listed on the community program listing. </p>
<br>
<a href="{auth_link}">Link</a>
<br>
<p>Regards,<br>
C4GT Support Bot</p>

</body>
</html>
'''
    return TopHTML

class NewRegistration:
    def __init__(self):
        return
    
    def send_email(self, subject, body, to_email, html=None):
        # Your email and application-specific password
        sender_email = 'c4gtsamagra@gmail.com'
        sender_password = 'kikejugtijfsmfrf'

        # Set up the email content
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = to_email
        if html:
            msg.add_alternative(html, subtype='html')

        # Send the email using SMTP
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.ehlo()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                print(f"Email sent to {to_email}!")
        except Exception as e:
            print(f"Error occurred: {e}")
    
    def createNewReg(self,data):
        html = generateHTMLForEmail(data["organisation"], data["email"], data["repos"], data["auth_link"])
        registrationMappingEmail = generateMappingTemplate(data["organisation"], data["email"], data["repos"])
        self.send_email("New Registration",'', "kanav@samagragovernance.in", html)
        self.send_email("Mapping Test", '', "kanav@samagragovernance.in", registrationMappingEmail)
        self.send_email("Mapping Test", '', "kanav@samagragovernance.in", registrationAknowledgementEmail)

        