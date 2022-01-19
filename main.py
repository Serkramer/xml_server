# -*- coding: utf-8 -*-
import requests as requests
import xml.etree.ElementTree as xml_xml
from flask import Flask, Response

app = Flask(__name__)

server = "http://192.168.11.190:8892"
server_auth = "http://192.168.11.190:8890"


def createXML(filename, answer, answer2):
    root = xml_xml.Element("data")

    client = xml_xml.Element("client")
    client.text = answer["payer"]["name"]
    root.append(client)

    printorg = xml_xml.Element("printorg")
    printorg.text = answer["printingCompany"]["name"]
    root.append(printorg)

    clientID = xml_xml.Element("clientID")
    clientID.text = answer["printingCompany"]["processId"]
    root.append(clientID)

    contactPerson = xml_xml.Element("contactPerson")
    root.append(contactPerson)

    contact_name = xml_xml.SubElement(contactPerson, "name")
    contact_name.text = answer2["contact"]["firstName"] + " " + answer2["contact"]["lastName"]

    contact_phone = xml_xml.SubElement(contactPerson, "phone")
    contact_phone.text = str(answer2["contact"]["mainNumber"]["value"])

    contact_email = xml_xml.SubElement(contactPerson, "email")
    contact_email.text = str(answer2["contact"]["mainMail"]["value"])

    workFileName = xml_xml.Element("workFileName")
    workFileName.text = answer["workFileName"]
    root.append(workFileName)

    filename_no_exp = str(answer["workFileName"]).split("."[0])

    fileNameNoExt = xml_xml.Element("fileNameNoExt")
    fileNameNoExt.text = filename_no_exp[0]
    root.append(fileNameNoExt)

    workname = xml_xml.Element("workname")
    workname.text = answer["name"]
    root.append(workname)

    deliveryInfo = xml_xml.Element("deliveryInfo")
    root.append(deliveryInfo)

    deliveryInfo_date = xml_xml.SubElement(deliveryInfo, "date")
    deliveryInfo_date.text = str(answer["orderDelivery"]["shippingDatePlaned"])

    deliveryInfo_time = xml_xml.SubElement(deliveryInfo, "time")

    deliveryInfo_method = xml_xml.SubElement(deliveryInfo, "method")
    deliveryInfo_method.text = answer["orderDelivery"]["deliveryType"]["type"]

    deliveryInfo_address = xml_xml.SubElement(deliveryInfo, "address")
    deliveryInfo_address.text = answer["orderDelivery"]["deliveryAddress"]

    deliveryInfo_contact = xml_xml.SubElement(deliveryInfo, "contact")
    deliveryInfo_contact.text = answer["orderDelivery"]["contact"]

    tech = xml_xml.Element("tech")
    root.append(tech)

    tech_name = xml_xml.SubElement(tech, "name")
    tech_name.text = answer["clicheTechnology"]["name"]

    tech_resolution = xml_xml.SubElement(tech, "resolution")
    tech_resolution.text = str(answer["clicheTechnology"]["lenFileResolution"]["resolution"])

    if answer["revertPrinting"] is True:
        reversePrinting = "true"
    elif answer["revertPrinting"] is False:
        reversePrinting = "false"
    else:
        reversePrinting = "&&"

    reverse_printing = xml_xml.Element("reversePrinting")
    reverse_printing.text = reversePrinting
    root.append(reverse_printing)

    if answer["orderCompression"]["type"] == "IN_WEIGHT":
        verticalDistortion = answer["orderCompression"]["value"]
        horisontalDistortion = 100
    elif answer["orderCompression"]["type"] == "IN_HEIGHT":
        verticalDistortion = 100
        horisontalDistortion = answer["orderCompression"]["value"]
    else:
        verticalDistortion = 100
        horisontalDistortion = 100

    distortion = xml_xml.Element("distortion")
    root.append(distortion)

    vertical_distortion = xml_xml.SubElement(distortion, "verticalDistortion")
    vertical_distortion.text = str(verticalDistortion)

    horisontal_distortion = xml_xml.SubElement(distortion, "horisontalDistortion")
    horisontal_distortion.text = str(horisontalDistortion)

    angleset = xml_xml.Element('angleset')
    angleset.text = answer["angleSet"]["name"]
    root.append(angleset)

    changeYellowRuling = xml_xml.Element('changeYellowRuling')
    changeYellowRuling.text = "no"
    root.append(changeYellowRuling)
    if answer["orderNotes"] is not None:
        notes = xml_xml.Element('notes')
        notes.text = answer["orderNotes"][0]["text"]
        root.append(notes)

    inks = xml_xml.Element('inks')
    root.append(inks)
    quantity = 0
    outputColors = ""
    for x in range(len(answer["orderPlaneSlices"])):
        ink = xml_xml.SubElement(inks, "ink")
        ink.set("name", answer["orderPlaneSlices"][x]["name"])
        ink.set("HEXcolor", answer["orderPlaneSlices"][x]["html"])
        inkName = xml_xml.SubElement(ink, "inkName")
        inkName.text = answer["orderPlaneSlices"][x]["name"]
        printingMethod = xml_xml.SubElement(ink, "printingMethod")
        printingMethod.text = answer["orderPlaneSlices"][x]["printingMethod"]
        ruling = xml_xml.SubElement(ink, "ruling")
        ruling.text = str(answer["orderPlaneSlices"][x]["ruling"]["id"])
        angle = xml_xml.SubElement(ink, "angle")
        angle.text = str(answer["orderPlaneSlices"][x]["angle"])
        material = xml_xml.SubElement(ink, "material")
        material.text = answer["material"]["name"]
        dot = xml_xml.SubElement(ink, "dot")
        dot.text = answer["orderPlaneSlices"][x]["rasterDot"]["code"]
        piece = xml_xml.SubElement(ink, "dot")
        piece.set("fragmentID", "0")
        piece.set("width", str(answer["orderPlaneSlices"][x]["width"]))
        piece.set("height", str(answer["orderPlaneSlices"][x]["height"]))
        piece.set("quaintity", str(answer["orderPlaneSlices"][x]["quantity"]))
        quantity += answer["orderPlaneSlices"][x]["quantity"]

        outputColors += answer["orderPlaneSlices"][x]["name"]
        if x < (len(answer["orderPlaneSlices"]) - 1):
            outputColors += ";"

    totals = xml_xml.Element('totals')
    root.append(totals)
    outputColors_names = xml_xml.SubElement(totals, "outputColorsNames")
    outputColors_names.text = outputColors
    outputColorsCount = xml_xml.SubElement(totals, "outputColorsCount")
    outputColorsCount.text = str(len(answer["orderPlaneSlices"]))
    totalFragmentsCount = xml_xml.SubElement(totals, "totalFragmentsCount")
    totalFragmentsCount.text = str(quantity)
    totalPolymerArea = xml_xml.SubElement(totals, "totalPolymerArea")
    totalPolymerArea.text = str(answer["formsArea"])

    username = xml_xml.Element('username')
    username.text = answer["login"]
    root.append(username)
    tree = xml_xml.ElementTree(root)
    return tree


@app.route('/<order_id>')
def get_order_info_for_rip(order_id):
    req = requests.request(method='GET', url=server + "/orders/" + order_id)
    answer = req.json()
    req2 = requests.request(method='GET', url=server_auth + "/info/get-by-login/" + answer["login"])
    answer2 = req2.json()
    xml_info = createXML("appt.xml", answer, answer2)
    text = '<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/xsl" href="file://fileserver/share/zvk/template.xsl"?>'
    resp = Response(text + xml_xml.tostring(xml_info.getroot(), encoding="UTF-8").decode("utf-8"))
    resp.headers['Content-Type'] = 'application/xml'
    return resp


if __name__ == '__main__':
    app.run(host='192.168.11.190')
