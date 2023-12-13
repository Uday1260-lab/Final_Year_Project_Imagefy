# Specifications

## Intro

The VMagnify application shall be a web application which permits to the user to display a picture in an higher resolution up to 4X the resolution of the image in input.

## Requirements

### General software requirements

#### Global Access

To permits a global access, the application shall be accessible from a browser.

#### Language

The application shall be coded in Python3.8+.

#### Web framework

The application shall use the Flask web framework.

#### Separation of pictures and videos

As the functioning is totally different, pictures and videos shall be in a separate page.

#### End of session

When the user terminates the session, all data shall be dumped.

### Pictures

#### Pictures UI

The pictures UI shall be conformant to ![Picture_UI_Specification](Picture_UI_Specification.png)

The pictures UI shall contains the following content :

- An URL text box to enter the URL of a picture on Internet.
- A button to validate the URL and start the processing of the resulting picture.
- A text box to display the image size.
- An image canvas to display the image.
- An image slider to zoom in/out on the picture.  

#### Validity of the URL

To be valid, the URL shall validate the following requirements:

1. The URL shall exist.
2. The URL shall be accessible without authentification.

After both requirements are validated, the picture file shall be verified.

#### Validity of the picture file

To be valid, the picture file shall validate the following requirements :

1. The file extension shall be a *.png or *.jpeg. (TBC)
2. The file shall be a picture file, other file types shall be ignored.
3. The picture format shall be RGB 24 bit.

After requirements are validated, the picture can be processed.

#### Processing of pictures

The processing of pictures shall be done after the user validates his picture choice.

#### Processing algorithm of pictures

As seen in [learnopencv.com](https://learnopencv.com/super-resolution-in-opencv/), processing of the pictures shall use the ESDR algorithm because it has the best signal/noise ratio.
