states = ['AL','AK','AZ','AR','CA','CO','CT','DC','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY',\
    'LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NYC','NC','ND','OH',\
    'OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY','PR','VI','GU','MP']
state_names = {'AL':'Alabama','AK':'Alaska','AZ':'Arizona','AR':'Arkansas','CA':'California'\
    ,'CO':'Colorado','CT':'Connecticut','DE':'Delaware','FL':'Florida','GA':'Georgia',\
    'HI':'Hawaii','ID':'Idaho','IL':'Illinois','IN':'Indiana','IA':'Iowa','KS':'Kansas'\
    ,'KY':'Kentucky','LA':'Louisiana','ME':'Maine','MD':'Maryland','MA':'Massachusetts',\
    'MI':'Michigan','MN':'Minnesota','MS':'Mississippi','MO':'Missouri','MT':'Montana',\
    'NE':'Nebraska','NV':'Nevada','NH':'New Hampshire','NJ':'New Jersey','NM':'New Mexico'\
    ,'NY':'New York','NYC':'New York City','NC':'North Carolina','ND':'North Dakota','OH':'Ohio','OK':'Oklahoma'\
    ,'OR':'Oregon','PA':'Pennsylvania','RI':'Rhode Island','SC':'South Carolina',\
    'SD':'South Dakota','TN':'Tennessee','TX':'Texas','UT':'Utah','VT':'Vermont','VA':'Virginia'\
    ,'WA':'Washington','WV':'West Virginia','WI':'Wisconsin','WY':'Wyoming','PR':'Puerto Rico',\
    'VI':'U.S. Virgin Islands','DC':'District of Columbia','GU':'Guam','MP':'Northern Mariana Islands'}
fips_codes = {'AL':'01','AK':'02','AZ':'04','AR':'05','CA':'06','CO':'08','CT':'09','DC':'11',\
    'DE':'10','FL':'12','GA':'13','HI':'15','ID':'16','IL':'17','IN':'18','IA':'19','KS':'20',\
    'KY':'21','LA':'22','ME':'23','MD':'24','MA':'25','MI':'26','MN':'27','MS':'28','MO':'29',\
    'MT':'30','NE':'31','NV':'32','NH':'33','NJ':'34','NM':'35','NY':'36','NC':'37','ND':'38',\
    'OH':'39','OK':'40','OR':'41','PA':'42','RI':'44','SC':'45','SD':'46','TN':'47','TX':'48',\
    'UT':'49','VT':'50','VA':'51','WA':'53','WV':'54','WI':'55','WY':'56','PR':'72','VI':'78',\
    'NYC':'-','GU':'14','MP':'69'}

text = ''
ix = 0
for state in states:
    if ix % 2 == 0:
        color = '#FFFFFF'
    else:
        color = '#C8C8C8'

    fips = fips_codes[state]

    statecell = '<tr bgcolor="%s">\n\t<th>%s</th>\n' % (color,state_names[state])
    # cumulative cases and deaths, daily cases and deaths, excess mortality
    if state == 'NY':
        cell1 = '\t<td><a href="/images/covid/log_cases_%s.png"><button type="button" class="btn btn-info"></button></a><br>(excluding NYC)</td>\n' % state.lower()
        cell2 = '\t<td><a href="/images/covid/cases_%s.png"><button type="button" class="btn btn-info"></button></a><br>(excluding NYC)</td>\n' % state.lower()
        cell3 = '\t<td><a href="/images/covid/deaths_%s.png"><button type="button" class="btn btn-info"></button></a><br>(excluding NYC)</td>\n' % state.lower()
        cell4 = '\t<td><a href="/images/covid/excess_%s.png"><button type="button" class="btn btn-info"></button></a><br>(exluding NYC)</td>\n' % state.lower()
    elif state in ['VI','GU','MP']:
        cell4 = '\t<td>(not available)</td>\n'
    else:
        cell1 = '\t<td><a href="/images/covid/log_cases_%s.png"><button type="button" class="btn btn-info"></button></a></td>\n' % state.lower()
        cell2 = '\t<td><a href="/images/covid/cases_%s.png"><button type="button" class="btn btn-info"></button></a></td>\n' % state.lower()
        cell3 = '\t<td><a href="/images/covid/deaths_%s.png"><button type="button" class="btn btn-info"></button></a></td>\n' % state.lower()
        cell4 = '\t<td><a href="/images/covid/excess_%s.png"><button type="button" class="btn btn-info"></button></a></td>\n' % state.lower()
    # occupied hospital beds, percent of hospital beds, positivity
    if state == 'NYC':
        cell5 = '\t<td>(not available)</td>\n'
        cell6 = '\t<td>(not available)</td>\n'
        cell7 = '\t<td>(not available)</td>\n'
        cell8 = '\t<td>(not available)</td>\n'
    else:
        cell5 = '\t<td><a href="/images/covid/beds_%s.png"><button type="button" class="btn btn-info"></button></a></td>\n' % state.lower()
        cell6 = '\t<td><a href="/images/covid/percent_%s.png"><button type="button" class="btn btn-info"></button></a></td>\n' % state.lower()
        cell7 = '\t<td><a href="/images/covid/testing_%s.png"><button type="button" class="btn btn-info"></button></a></td>\n' % state.lower()
        cell8 = '\t<td><a href="/images/covid/positivity_%s.png"><button type="button" class="btn btn-info"></button></a></td>\n' % state.lower()
    # county maps
    if state in ['DC','PR','VI','NYC','GU','MP']:
        cell9 = '\t<td>(not available)</td>\n</tr>\n'
    else:
        cell9 = '\t<td><a href="/images/covid/countymaps/cases_%s.png"><button type="button" class="btn btn-info"></button></a></td>\n</tr>\n' % fips

    text = text+statecell+cell1+cell2+cell3+cell4+cell5+cell6+cell7+cell8+cell9

    ix += 1

outfile = open('htmltext.txt','w')
n = outfile.write(text)
outfile.close()
