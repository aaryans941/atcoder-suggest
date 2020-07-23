import os , sys, requests, random, time
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
    

    def return_json_from_url(url):
        try:
            res = requests.get(url)
            time.sleep(1)
            return res.json()
        except:
            return False
    
    def return_user_submissions(user_id):
        return return_json_from_url('https://kenkoooo.com/atcoder/atcoder-api/results?user=' + user_id)
    
    def return_all_contest_list():
        return return_json_from_url('https://kenkoooo.com/atcoder/resources/contests.json')

    def return_solved_dict(user_id_list):
        solved_dict = {} 
        for user_id in user_id_list.split(';'):
            user_submissions = return_user_submissions(user_id)
            for sub in user_submissions:
                if sub['result'] == 'AC':
                    solved_dict[sub['problem_id']] = sub['result']
                else:
                    solved_dict[sub['problem_id']] = sub['result']
        return solved_dict

    def return_contest_participation_list(user_id_list):
        contest_participation_dict = {} 
        for user_id in user_id_list.split(';'):
            user_submissions = return_user_submissions(user_id)
            for sub in user_submissions:
                if sub['result'] == 'AC':
                    contest_participation_dict[sub['contest_id']] = sub['result']
                else:
                    contest_participation_dict[sub['contest_id']] = sub['result']
        return contest_participation_dict
    
    def return_local_json(file_name):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_path = os.path.join(SITE_ROOT, 'static/data', file_name)
        return json.load(open(json_path))
    
    def return_contest_json(contest_id):
        contest = {
                'id' : contest_id,
                'url' : '/'.join(['https://atcoder.jp' , 'contests' , contest_id]), 
                }
        return contest

    def return_problem_json(problem_id , contest_id , rating):
        problem = {
            'id': problem_id,
            'contest_id': contest_id,
            'return_contest_participation_listing': rating,
            'url': '/'.join(['https://atcoder.jp' , 'contests' , contest_id , 'tasks' , problem_id]),
            }
        return problem 
    
    @app.route('/gimme/<user_id_list>/')
    @app.route('/gimme/<user_id_list>/lower=<int:lb>')
    @app.route('/gimme/<user_id_list>/upper=<int:ub>')
    @app.route('/gimme/<user_id_list>/lower=<int:lb>&&upper=<int:ub>')
    def get_suggestions(user_id_list, lb = -6000, ub = 6000):
        solved_dict  = return_solved_dict(user_id_list)
        problem_list = return_local_json('merged-problems.json')
        difficulty_dict = return_local_json('problem-models.json')
        unsolved_problem_list = []
        for problem in problem_list:
            if problem['id'] not in solved_dict:
               if problem['id'] in difficulty_dict and 'difficulty' in difficulty_dict[problem['id']] and difficulty_dict[problem['id']]['difficulty'] is not None:
                    rating = float(difficulty_dict[problem['id']]['difficulty'])
                    if rating >= lb and rating <= ub:
                        suitable_problem = return_problem_json(problem['id'] , problem['contest_id'] , int(rating))
                        unsolved_problem_list.append(suitable_problem)
        random.shuffle(unsolved_problem_list)
        result_count = min(len(unsolved_problem_list) , 10)
        unsolved_problem_list = unsolved_problem_list[:result_count]
        
        return render_template_string('''
            <table>
                    <tr>
                        <th> S.No. </th>
                        <th> Problem ID </th> 
                        <th> Contest ID </th>
                        <th> Difficulty </th>
                        <th> Url </th>
                   </tr>

              
            {% for sno, problem in unsolved_problem_list%}

                    <tr>
                        <td>{{ sno }}
                        <td>{{ problem['id'] }}</td> 
                        <td>{{ problem['contest_id'] }}</td> 
                        <td>{{ problem['rating'] }}</td> 
                        <td> <a href={{problem['url']}}> link </a> </td>
                    </tr>

            {% endfor %}


            </table>
        ''', unsolved_problem_list=enumerate(unsolved_problem_list))
    

    @app.route('/vc/<user_id_list>/')
    @app.route('/vc/<user_id_list>/<filter_string>')
    def get_virtual_contests(user_id_list, filter_string):
        contest_participation_dict = return_contest_participation_list(user_id_list)
        contest_list = return_all_contest_list()
        unsolved_contest_list = [] 
        for contest in contest_list:
            if filter_string not in contest['id'] or contest['id'] in contest_participation_dict:
                continue 
            unsolved_contest_list.append(return_contest_json(contest['id']))            
        random.shuffle(unsolved_contest_list)
        result_count = min(len(unsolved_contest_list) , 10)
        unsolved_contest_list = unsolved_contest_list[:result_count]
        
        return render_template_string('''
            <table>
                    <tr>
                        <th> S.No. </th>
                        <th> Contest ID </th>
                        <th> Url </th>
                   </tr>

              
            {% for sno, contest in unsolved_contest_list%}

                    <tr>
                        <td>{{ sno }}
                        <td>{{ contest['id'] }}</td> 
                        <td> <a href={{ contest['url'] }}> link </a> </td>
                    </tr>

            {% endfor %}


            </table>
        ''', unsolved_contest_list=enumerate(unsolved_contest_list))

    return app

