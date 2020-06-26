import os , sys, requests, random
from flask import Flask, render_template_string, url_for, jsonify, json

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SECRET_KEY='dev',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
        # load the instance config, if it exists, when not testingi
    else:
        app.config.from_pyfile(test_config)

    # ensure instance folder exists

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    

    def get_json(url):
        try:
            res = requests.get(url)
            return res.json()
        except:
            return False
    
    def return_user_submissions(user_id):
        url = 'https://kenkoooo.com/atcoder/atcoder-api/results?user='
        url = url + user_id
        return get_json(url)

    def return_solved_dict(user_id):
        user_submissions = return_user_submissions(user_id)
        solved_dict = {} 
        for sub in user_submissions:
            if sub['result'] == 'AC':
                solved_dict[ sub['problem_id'] ] = sub['result']
            elif sub['problem_id'] not in solved_dict:
                solved_dict[ sub['problem_id'] ] = sub['result']
        return solved_dict


    def return_local_json(file_name):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, 'static/data', file_name)
        return json.load(open(json_url))
        
    def get_problem_json(problem_id , contest_id , rating):
        problem = {}
        problem['id'] = problem_id
        problem['contest_id'] = contest_id
        problem['rating'] = rating
        problem['url'] = os.path.join('https://atcoder.jp' , 'contests' , contest_id , 'tasks' , problem_id)
        return problem 

    @app.route('/user/<user_id>/')
    @app.route('/user/<user_id>/lower=<int:lb>')
    @app.route('/user/<user_id>/upper=<int:ub>')
    @app.route('/user/<user_id>/lower=<int:lb>&&upper=<int:ub>')
    def func(user_id, lb = 0 , ub = 8000):
        solved_dict  = return_solved_dict(user_id)
        problem_list = return_local_json('merged-problems.json')
        difficulty_dict = return_local_json('problem-models.json')
        unsolved_list = []
        for problem in problem_list:
            if problem['id'] in solved_dict and problem['id'] != 'AC':
                #print(problem['id'] , file=sys.stderr)
                continue
            else:
                if problem['id'] not in difficulty_dict or 'difficulty' not in difficulty_dict[problem['id']] or difficulty_dict[problem['id']]['difficulty'] is None:
                    continue
                else:
                    rating = float(difficulty_dict[problem['id']]['difficulty'])
                if rating >= lb and rating <= ub:
                    suitable_problem = get_problem_json(problem['id'] , problem['contest_id'] , int(rating))
                    unsolved_list.append(suitable_problem)

        random.shuffle(unsolved_list)
        result_count = min(len(unsolved_list) , 10)
        unsolved_list = unsolved_list[0:result_count - 1]
#        return jsonify(solved_dict)

        
        return render_template_string('''
            <table>
                    <tr>
                        <th> S.No. </th>
                        <th> Problem ID </th> 
                        <th> Contest ID </th>
                        <th> Difficulty </th>
                        <th> Url </th>
                   </tr>

              
            {% for sno, problem in unsolved_list%}

                    <tr>
                        <td>{{ sno }}
                        <td>{{ problem['id'] }}</td> 
                        <td>{{ problem['contest_id'] }}</td> 
                        <td>{{ problem['rating'] }}</td> 
                        <td> <a href={{problem['url']}}> link </a> </td>
                    </tr>

            {% endfor %}


            </table>
        ''', unsolved_list=enumerate(unsolved_list))
    return app

