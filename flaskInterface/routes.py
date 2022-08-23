from flask import  render_template,flash, redirect, url_for, request 
from flaskInterface.forms import RegistrationForm, LoginForm, TaskProcessorForm,DomainForm, ServiceRegistrationForm
from flaskInterface.models  import Domain, TaskProcessor, User, ServiceRegister
from flaskInterface import app,db, bcrypt
from flask_admin import Admin 
from flask_login import login_user, current_user, logout_user,login_required
import pandas  as pd 
import os, secrets 
from werkzeug.utils import secure_filename
from datetime import datetime
# admin = Admin(app, name='microblog', template_mode='bootstrap3')
# admin.add_view(ModelView(User, db.session))
# admin.add_view(TaskView(Task, db.session))
# admin.add_view(DomainView(Domain, db.session))

from  .components  import agent  
from  .components.serviceReg import greateMSGraph,create_pipeline, Create_input_spec, Create_output_spec



storage = './flaskInterface/storage/files'
def saveUploads(Fname):
    random_hex = secrets.token_hex(8)
    print(Fname)
    _, f_ext = os.path.splitext(Fname)
    file_rn =  random_hex + f_ext
    print(file_rn)
    file_path  = os.path.join(app.root_path,'static/datas', f'{file_rn}')

    return file_path

@app.route('/')
@app.route('/home')
def Home():
    return render_template('home.html')


@app.route('/login',methods=['GET','POST'])
def Login(): 

    if current_user.is_authenticated:
        return  redirect(url_for('Home'))

    form =LoginForm()

    if form.validate_on_submit():
        user =  User.query.filter_by(email=form.email.data).first()
    
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user,remember=form.remember.data )
            
            print("successfully logged in")
            return redirect(url_for('Home'))

        else:
            flash('Login unsuccessful. please  check username and password', 'danger')

    print(form.errors)
    return render_template('login.html',title='Login', form=form)


@app.route('/register', methods=['POST','GET'])
def register():
    if current_user.is_authenticated:
        return  redirect(url_for('Home'))
    form =  RegistrationForm()


    if form.validate_on_submit():
        pass1 =  form.password1.data
        pass2 =  form.password2.data 
        if pass1 ==  pass2:
            hashed_password =  bcrypt.generate_password_hash(form.password2.data).decode('utf8')
            user =  User(username =form.username.data , email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()

            flash ('Your account has been created! you are now able to log in ', 'success')
            return redirect(url_for('Login'))

    return render_template('register.html',title='Register', form=form)


@app.route('/addtask', methods=['GET','POST'])
@login_required
def Task():
    form =  TaskProcessorForm()
    print(current_user.username)
    if form.validate_on_submit():
    
        
      
      
        my_file = request.files['fileInput']
      
        f =  form.fileInput.data.filename 
        req =  request.files['fileInput']
        data = form.fileInput.data 

            
        path2save =  os.path.join(storage,f)
        if os.path.isfile(path2save):
            prev =  path2save.rsplit('.',1)
            path2save = prev[0]+'_'+secrets.token_hex(4)+'.'+prev[1]
            req.save(path2save)
        else:
            req.save(path2save)
        
        task  = TaskProcessor(Ms_Name=form.Ms_name.data,
        Namespace=form.NameSpace.data , purpose=form.purpose.data,
        domain=form.domain.data , FField=path2save, desired_output=form.desired_output.data,
        created_by=current_user.username)
        
        

    #    form.fileInput.data.filename
    #    
        db.session.add(task)
        db.session.commit()

        task_name =  form.Ms_name.data
        namespace =  form.NameSpace.data
        purpose =  form.purpose.data
        domain =  form.domain.data 
        desire_O = list(form.desired_output.data)
        
        print(task_name)
        print(namespace)
        print(purpose)
        print(domain)
        print(desire_O)


        agent.OperatingTask(task_name=task_name,input_file_path=path2save,desir_output_type=desire_O,task_domain=domain,namespace=namespace, purpose=purpose)

      
        
        # print(path2save)
        # Dataframe =  pd.read_csv(path2save)
        # print(Dataframe.head())
    
    # print(form.errors)
    return render_template('addTask.html',title='jobs', form=form)
    
@app.route('/domain',methods=['GET','POST'])
@login_required
def Dom():

    form =  DomainForm()
    if form.validate_on_submit():
        domain =  Domain(title=form.title.data, description=form.description.data)
        db.session.add(domain)
        db.session.commit()
        flash(f'New Domain Added')
        


    return render_template('addDomain.html',title='jobs', form=form)

@app.route('/logout', methods=['GET','POST'])
def logout():

    logout_user()

    return redirect(url_for('Home'))

@app.route('/serviceregistration', methods=['GET','POST'])
def Servicereg():
    form = ServiceRegistrationForm() 
    
    if form.validate_on_submit():
        
        service_reg = ServiceRegister(Ms_name= form.Ms_name.data,Namespace=form.Namespace.data, Description=form.Description.data, Ms_type=form.Ms_type.data , Dependencies=form.Dependencies.data, Framework=form.Framework.data, GPU=form.GPU.data, Pipeline=form.Pipeline.data,Model_format=form.Model_format.data, Invoke_uri=form.Invoke_uri.data,Input_sp=form.Input_sp.data, Output_sp=form.Output_sp.data, Contributor=form.Contributor.data, License=form.License.data, Service_category= form.ServiceCategory.data)

        Ms_name=form.Ms_name.data 
        Namespace=form.Namespace.data
        Description =  form.Description.data 
        Dependencies =  form.Dependencies.data
        Framework =  form.Framework.data
        GPU= form.GPU.data
        Ms_type =  form.Ms_type.data 
        Pipeline =  form.Pipeline.data 
        Model_format =  form.Model_format.data 
        Invoke_uri =  form.Invoke_uri.data 
        Input_sp =  form.Input_sp.data 
        Output_sp =  form.Output_sp.data
        Contributor =  form.Contributor.data 
        License =  form.License.data 
        Service_category =  form.ServiceCategory.data 

       #breaking down all the output_spec 
        Output_sp = Create_output_spec(Output_sp)
        Input_sp =  Create_input_spec(Input_sp)
        Pipeline =  create_pipeline(Pipeline)
        # removing whitespacesfrom  service_category to make URI Valid
        Service_category =  Service_category.replace(' ','_')
       



        greateMSGraph(Namespace,Ms_name,Description,Ms_type,Dependencies,Framework,GPU,Pipeline,Model_format,Input_sp,Output_sp,Contributor,License,Service_category)

        

        print(form.errors)

        db.session.add(service_reg)
        db.session.commit() 
        flash(f'Service Successfully Registered','success')

        print(Input_sp)
        print(Output_sp)
        print(GPU)
        print(Dependencies)

    return render_template('service_registration.html', form=form)