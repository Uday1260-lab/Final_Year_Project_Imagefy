"""
app.py : main file of our application.
"""
import base64
import io
import os
import cgi
from datetime import datetime
from dash import Dash, html, dcc, Input, Output, State, callback_context
from dash.dependencies import Input, Output
import dash_daq as daq
import dash_bootstrap_components as dbc
from imagefy.imagefy_picture import IMagefyPicture

# app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = Dash(__name__, external_stylesheets=['static/styles/styles.css'])
LOGO_FILENAME = "static/img/logo/IMagefy50.png"
SAVE_IMAGE_DIRECTORY = "static/img/downloads"

# Test 1 Butterfly 
DEFAULT_URL = "https://raw.githubusercontent.com/Saafke/EDSR_Tensorflow/master/images/input.png"
DEFAULT_FILENAME = "static/img/example/test1.png"

# Test 2 Car
# DEFAULT_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/2018_Suzuki_Karimun_Wagon_R_GL_%28front%29.jpg/320px-2018_Suzuki_Karimun_Wagon_R_GL_%28front%29.jpg"
# DEFAULT_FILENAME = "static/img/example/test2.png"

# Test3 Dog
# DEFAULT_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Labrador_on_Quantock_%282175262184%29.jpg/320px-Labrador_on_Quantock_%282175262184%29.jpg"
# DEFAULT_FILENAME = "static/img/example/test3.png"

# Test4 Cat
# DEFAULT_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Orange_tabby_cat_sitting_on_fallen_leaves-Hisashi-01A.jpg/180px-Orange_tabby_cat_sitting_on_fallen_leaves-Hisashi-01A.jpg"
# DEFAULT_FILENAME = "static/img/example/test4.png"

logo_encoded = base64.b64encode(open(LOGO_FILENAME, 'rb').read())
imagefy = IMagefyPicture()
app.layout = html.Div(
    [
        html.Img(
            id="picture_logo",
            src='data:image/png;base64,{}'.format(logo_encoded.decode())
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            html.Div([
                                dcc.Upload(
                                    id='upload_image',
                                    children=html.Div([
                                    'Drag and Drop or ',
                                    html.A('Select Files')
                                    ]),
                                style={
                                    'width': '50%',
                                    'height': '60px',
                                    'lineHeight': '60px',
                                    'borderWidth': '2px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'marginTop': '10px',
                                    'marginBottom': '10px',
                                    'marginRight': 'auto',
                                    'marginLeft': 'auto',
                                    'backgroundColor': 'white'
                                },
                                multiple=False),
                                html.Div(id='output_image_upload'),
                            ])
                        ),
                        dbc.Row(
                            html.Div(
                                html.Button(
                                    "Submit Image",
                                    id="submit_image"
                                )
                            )
                        ),
                        dbc.Row(
                            html.Div(
                                html.Label(
                                    "Or Enter Image URL"
                                )
                            )
                        ),
                        dbc.Row(
                            html.Div(
                                dcc.Input(
                                    id="picture_url",
                                    type="url",
                                    size="100",
                                    value=DEFAULT_URL
                                )
                            )
                        ),
                        dbc.Row(
                            html.Div(
                                html.Button(
                                    "Submit URL",
                                    id="submit_url"
                                )
                            )
                        ),
                        # dbc.Row(
                        #     html.Details([
                        #         html.Summary('Parameters Tab(Click To Show!!!)'),
                        #             html.Div([
                        #                 html.Table(id='Tab-keeper',),
                        #             ])
                        #     ])
                        # ),
                        dbc.Row(
                            html.Div(
                                html.Label(
                                    "Picture Zoom Slider"
                                )
                            )
                        ),
                        dbc.Row(
                            html.Div(
                                daq.Slider(
                                    id="picture_zoom",
                                    min=1,
                                    max=4,
                                    value=1,
                                    handleLabel={
                                        "showCurrentValue": True,
                                        "label": "UPSCALE"
                                    },
                                    step=1,
                                    color="red",
                                    labelPosition='bottom',
                                    marks={
                                        '1': '1x',
                                        '2': '2x',
                                        '3': '3x',
                                        '4': '4x'
                                    }
                                )
                            )
                        )
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            html.Div(
                                html.Img(
                                    id="displayed_picture",
                                    src=DEFAULT_FILENAME
                                )
                            )
                        ),
                        dbc.Row(
                            html.Div(
                                html.Label(
                                    "Picture Resolution"
                                )
                            )
                        ),
                        dbc.Row(
                            html.Div(
                                dcc.Input(
                                    id="picture_infos",
                                    type="text",
                                    size="100",
                                    readOnly=True
                                )
                            )
                        )
                    ]
                )
            ]
        )
    ]
)


    
def parse_contents(contents, filename, date):
    return html.Div([
        html.Div('Raw Content:'),
        html.H5(filename),
        html.Img(id="uploaded_picture",src=contents)
    ])

@app.callback(
    Output('output_image_upload', 'children'),
    Input('upload_image', 'contents'),
    State('upload_image', 'filename'),
    State('upload_image', 'last_modified')
)

def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(list_of_contents, list_of_names, list_of_dates)]
        return children

@app.callback(
    Output(component_id='displayed_picture', component_property='src'),
    Output(component_id='picture_infos', component_property='value'),
    Input(component_id='submit_url', component_property='n_clicks'),
    Input(component_id='submit_image', component_property='n_clicks'),
    State(component_id='picture_url', component_property='value'),
    Input(component_id='picture_zoom', component_property='value'),
    State('upload_image', 'filename'),
    Input('upload_image', 'contents')
)
def process(submit_url, submit_image, picture_url, picture_zoom, upload_image_filename, upload_image):
    """ process the inputs, because we use the same outputs, we have to use a shared callback """
    
    ctx = callback_context

    # ctx variable permits to know which input triggered
    if not ctx.triggered:
        # this condition triggers on start        
        imagefy.process_url(picture_url)
        return imagefy.get_picture_data(picture_zoom-1)    
    else:
        triggered_item = ctx.triggered[0]['prop_id'].split('.')[0]

    # triggered_item = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_item == "submit_url":
        return imagefy.process_url(picture_url)
    
    elif triggered_item == "submit_image":

        if upload_image is not None:
            current_datetime = datetime.now()
            data = upload_image.encode("utf8").split(b";base64,")[1]
            print(data)
            with open(os.path.join(SAVE_IMAGE_DIRECTORY, upload_image_filename), "wb") as fp:
                fp.write(base64.decodebytes(data))
            _, file_extension = os.path.splitext(os.path.join(SAVE_IMAGE_DIRECTORY, upload_image_filename))
            new_file_name = current_datetime.strftime("%Y_%m_%d_%H_%M_%S") + file_extension
            os.rename(os.path.join(SAVE_IMAGE_DIRECTORY, upload_image_filename), os.path.join(SAVE_IMAGE_DIRECTORY, new_file_name))

        return imagefy.process_saved_image(os.path.join(SAVE_IMAGE_DIRECTORY, new_file_name))
    
    elif triggered_item == "picture_zoom":
        return imagefy.get_picture_data(picture_zoom-1)

def get_file_extension(content_type):
    _, content_type_info = cgi.parse_header(content_type)
    return content_type_info.get('name').split('.')[-1]

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run_server()