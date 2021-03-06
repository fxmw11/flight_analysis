def build_string_query(field, op, values, logic_conj):
    query = ''
    for v in values:
        query += f"{field}.str.{op}('{v}') {logic_conj} "
    return query[:-(2+len(logic_conj))]


def drop_irrelevant_data(df, irrelevant_manu):

    # # without dividing the query in multiple parts  we get 's_push: parser stack overflow'
    # # ->  The Python parser has a depth limit somewhere between 92 and 99 when parsing an expression
    # for i in range(len(irrelevant_manu) // 90 + 1):
    #     query = ''
    #     manu_part = irrelevant_manu[i*90:min((i+1)*90, len(irrelevant_manu))]
    #     for manu in manu_part:
    #         manu_clean = manu.replace("\'", "\\\'")
    #         query += f"manufacturername != '{manu_clean}' and "
    #     df = df.query(query[:-5], engine='python') # use engine='python', otherwise error 'too many inputs' occurs (NPY_MAXARGS=32)

    # drop manufacturers where we do not have any mtow data
    df = df.query("manufacturername not in @irrelevant_manu") # faster than using "a != b and ..." + avoids stack overflow

    # drop manufacturernames of small/light weight or military only aircrafts
    manus = ['Agusta', 'Airbus Helicopters', 'Balloon', 'Bell', 'Ercoupe', 'Eurocopter', 'Flugzeugbau', 'Fuji',
             'Grob', 'Grumman', 'Honda', 'Hughes', 'Kawasaki', 'Leonardo', 'mbb', 'MBB', 'Murphy', 'Murr', 'Northrop',
             'Remos', 'Robin', 'Saab', 'Sikorsky', 'Stearman', 'Swearingen', 'Tecna', 'Tupolev', 'Vulcanair']
    query = build_string_query('manufacturername', 'contains', manus, 'or')
    query += " or manufacturername == 'Sukhoi'"
    query += " or manufacturername.str.startswith('Van')"
    df_not = df.query(query, engine='python')  # use engine='python', to enable str contains
    df = df.drop(df_not.index, axis=0)

    # drop some model without mtow
    query = "model.str.contains('Globemaster') or "
    query += "model.str.contains('C-17') or "
    query += "model.str.contains('Huron') or "
    subquery = build_string_query('model', 'startswith', ['PT-', 'KC-', 'B-', 'C-', 'C97', 'E-', 'F-', 'FA-'], 'or')
    query += f"(manufacturername.str.contains('Boeing') and ({subquery})) or "
    subquery = build_string_query('model', 'contains', ['PA-1[1-7]', 'PA-2[0-3]', 'PA-30'], 'or')
    query += f"(manufacturername.str.contains('Piper') and ({subquery}))"
    df_not = df.query(query, engine='python')  # use engine='python', to use str contains
    df = df.drop(df_not.index, axis=0)

    return df


def add_alternatives(df, manu_col, model_col):
    df['manu_alt'] = ''
    df['model_alt'] = ''

    cache = {}
    def add_manu_alt(search, alt=None):
        if alt is None:
            alt = search
        rows = df[manu_col].str.contains(search, case=False)
        df.loc[rows, 'manu_alt'] = alt
        if alt in cache.keys():
            cache[alt] = cache[alt] | rows
        else:
            cache[alt] = rows
    def add_model_alt(search, manu, alt=None):
        if alt is None:
            alt = search

        if manu in cache.keys():
            ind_manu = cache[manu]
        else:
            ind_manu = df[manu_col] == manu

        rows = df.loc[ind_manu, model_col].str.contains(search, case=False)
        df.loc[rows.index[rows], 'model_alt'] = alt
        pass
    def replace_model(search, replace, manu):
        if manu in cache.keys():
            ind_manu = cache[manu]
        else:
            ind_manu = df[manu_col] == manu
        df.loc[ind_manu, model_col] = df.loc[ind_manu, model_col].str.replace(search, replace)

    add_manu_alt('Aeritalia')
    add_manu_alt('Aeronca')
    add_manu_alt('Aerospatiale')
    add_manu_alt('Airbus')
    add_manu_alt('Air Tractor')
    add_manu_alt('American Champion')
    add_manu_alt('ATR')
    add_manu_alt('Avions De Transport Regional', 'ATR')
    add_manu_alt('Antonov')
    add_manu_alt('BAC', 'British Aircraft')
    add_manu_alt('Beech', 'Beechcraft')
    add_manu_alt('Beechcraft')
    add_manu_alt('Boeing')
    add_manu_alt('Boieng', 'Boeing')
    add_manu_alt('Bombardier')
    add_manu_alt('British Aircraft')
    add_manu_alt('British Aerospace')
    add_manu_alt('Britten-Norman')
    add_manu_alt('Canadair', 'Bombardier')
    add_manu_alt('Cessna')
    add_manu_alt('Cirrus')
    add_manu_alt('Comac')
    add_manu_alt('Convair')
    add_manu_alt('Daher')
    add_manu_alt('Dassault')
    add_manu_alt('De Havilland', 'Bombardier')
    add_manu_alt('Diamond')
    add_manu_alt('Dornier')
    add_manu_alt('Eclipse')
    add_manu_alt('Empresa Brasileira', 'Embraer')
    add_manu_alt('Embraer')
    add_manu_alt('Fairchild')
    add_manu_alt('Flight Design')
    add_manu_alt('Fokker')
    add_manu_alt('Gates', 'Bombardier')
    add_manu_alt('Glasair')
    add_manu_alt('Grumman')
    add_manu_alt('Gulfstream')
    add_manu_alt('Hawker', 'Beechcraft')
    add_manu_alt('Hoac', 'Diamond')
    add_manu_alt('Ilyushin')
    add_manu_alt('Israel')
    add_manu_alt('Learjet', 'Bombardier')
    add_manu_alt('LET')
    add_manu_alt('Lockheed')
    add_manu_alt('McDonnell Douglas', 'Boeing')
    add_manu_alt('Mooney')
    add_manu_alt('Morris Motor', 'Bombardier')
    add_manu_alt('Partenavia')
    add_manu_alt('Piaggio')
    add_manu_alt('Pilatus')
    add_manu_alt('Piper')
    add_manu_alt('Raytheon', 'Beechcraft')
    add_manu_alt('Reims', 'Cessna')
    add_manu_alt('Rockwell')
    add_manu_alt('Socata', 'Daher')
    add_manu_alt('Societe De Constr', 'Daher')
    add_manu_alt('Spacelines')
    add_manu_alt('Sud Aviation', 'Aerospatiale')
    add_manu_alt('Sukhoi')
    add_manu_alt('Stinson')
    add_manu_alt('Textron', 'Cessna')
    add_manu_alt('Trexton', 'Cessna')
    add_manu_alt('Viking', 'Bombardier')

    repl = lambda matches: f"{matches.group(1)}-"
    replace_model('([0-9]{3}) ', repl, 'Airbus')
    replace_model('([0-9]{3}) ', repl, 'Boeing')
    replace_model('([0-9]{3})NG ', repl, 'Boeing')
    replace_model('(DHC-[0-9]{1}) ', repl, 'Bombardier')
    # repl = lambda matches: f"A{matches.group(1)}"
    # replace_model('([0-9]{3}-)', repl, 'Airbus')
    # repl = lambda matches: f"C{matches.group(1)}"
    # replace_model('([0-9]{3})', repl, 'Cessna')
    repl = lambda matches: f"{matches.group(1)}-{matches.group(2)}"
    replace_model('(BD) ?([0-9]{3})', repl, 'Bombardier')
    replace_model('(CL) ?([0-9]{3})', repl, 'Bombardier')
    replace_model('([TBM]{2,}) ?([0-9]{2,})', repl, 'Daher')
    replace_model('(DA) ?([0-9]{2})', repl, 'Diamond')
    replace_model('(EMB) ([0-9]{3})', repl, 'Embraer')
    replace_model('ERJ', 'EMB', 'Embraer')
    replace_model('(PA) ?([0-9]{2})', repl, 'Piper')
    replace_model('Standard', 'STD', 'Embraer')
    replace_model('Gulfstream', 'G', 'Gulfstream')
    replace_model('G-', 'G', 'Gulfstream')
    df.loc[df[manu_col].str.contains('Learjet'), model_col] = 'Learjet ' + df.loc[df[manu_col].str.contains('Learjet'), model_col]


    add_model_alt('222', 'Aeritalia')
    add_model_alt('7AC', 'Aeronca')
    add_model_alt('7EC', 'Aeronca')
    add_model_alt('11', 'Aeronca')
    add_model_alt('15', 'Aeronca')
    add_model_alt('210', 'Aerospatiale', 'Caravelle')
    add_model_alt('262', 'Aerospatiale', 'Nord')
    add_model_alt('601', 'Aerospatiale', 'Corvette')
    add_model_alt('Caravelle', 'Aerospatiale')
    add_model_alt('Corvette', 'Aerospatiale')
    add_model_alt('Nord', 'Aerospatiale')
    add_model_alt('220', 'Airbus')
    add_model_alt('300-1', 'Airbus')
    add_model_alt('300-2', 'Airbus')
    add_model_alt('300-6', 'Airbus')
    add_model_alt('300-600R', 'Airbus')
    add_model_alt('300-600ST', 'Airbus')
    add_model_alt('300-600XL', 'Airbus')
    add_model_alt('BelugaST', 'Airbus', '300-600ST')
    add_model_alt('BelugaXL', 'Airbus', '300-600XL')
    add_model_alt('300-B4-6', 'Airbus', '300-6')
    add_model_alt('300-C4-6', 'Airbus', '300-6')
    add_model_alt('300-F4-6', 'Airbus', '300-6')
    add_model_alt('310-2', 'Airbus')
    add_model_alt('310-3', 'Airbus')
    add_model_alt('318', 'Airbus')
    add_model_alt('319', 'Airbus')
    add_model_alt('320', 'Airbus')
    add_model_alt('320neo', 'Airbus')
    add_model_alt('321', 'Airbus')
    add_model_alt('321-1', 'Airbus')
    add_model_alt('321-2', 'Airbus')
    add_model_alt('321neo', 'Airbus')
    add_model_alt('330', 'Airbus')
    add_model_alt('340-2', 'Airbus')
    add_model_alt('340-3', 'Airbus')
    add_model_alt('340-5', 'Airbus')
    add_model_alt('340-6', 'Airbus')
    add_model_alt('350-1', 'Airbus')
    add_model_alt('350-8', 'Airbus')
    add_model_alt('350-9', 'Airbus')
    add_model_alt('380-80', 'Airbus')
    add_model_alt('380-84', 'Airbus')
    add_model_alt('400', 'Airbus')
    add_model_alt('ACJ', 'Airbus')
    add_model_alt('7', 'American Champion')
    add_model_alt('8', 'American Champion')
    add_model_alt('An-12', 'Antonov')
    add_model_alt('An-26', 'Antonov')
    add_model_alt('An-72', 'Antonov', 'An-74')
    add_model_alt('An-74', 'Antonov')
    add_model_alt('An-124', 'Antonov')
    add_model_alt('An-140', 'Antonov')
    add_model_alt('An-225', 'Antonov')
    add_model_alt('42', 'ATR')
    add_model_alt('72', 'ATR')
    add_model_alt('18', 'Beechcraft')
    add_model_alt('55', 'Beechcraft', 'Baron')
    add_model_alt('56', 'Beechcraft', 'Baron')
    add_model_alt('58', 'Beechcraft', 'Baron')
    add_model_alt('60', 'Beechcraft', 'Duke')
    add_model_alt('65', 'Beechcraft', 'Queen')
    add_model_alt('95', 'Beechcraft')
    add_model_alt('121', 'Beechcraft') # Hawker-Siddeley HS 121 Trident
    add_model_alt('125', 'Beechcraft') # Hawker-Siddeley HS 125 Series
    add_model_alt('400', 'Beechcraft')
    add_model_alt('600', 'Beechcraft')
    add_model_alt('700', 'Beechcraft')
    add_model_alt('748', 'Beechcraft') # Hawker-Siddeley 748
    add_model_alt('780', 'Beechcraft') # Hawker-Siddeley HS 780 Andover
    add_model_alt('800', 'Beechcraft')
    add_model_alt('801', 'Beechcraft') # Hawker-Siddeley HS 801 Nimrod
    add_model_alt('850', 'Beechcraft')
    add_model_alt('900', 'Beechcraft')
    add_model_alt('4000', 'Beechcraft') # Hawker Horizon
    add_model_alt('Argosy', 'Beechcraft') # Hawker-Siddeley Argosy
    add_model_alt('Trident', 'Beechcraft', '121') # Hawker-Siddeley HS 121 Trident
    add_model_alt('Series', 'Beechcraft', '125') # Hawker-Siddeley HS 125 Series
    add_model_alt('Andover', 'Beechcraft', '780') # Hawker-Siddeley HS 125 Series
    add_model_alt('Nimrod', 'Beechcraft', '801') # Hawker-Siddeley HS 801 Nimrod
    add_model_alt('A36', 'Beechcraft', 'Bonanza')
    add_model_alt('F33', 'Beechcraft', 'Bonanza')
    add_model_alt('G35', 'Beechcraft', 'Bonanza')
    add_model_alt('G36', 'Beechcraft', 'Bonanza')
    add_model_alt('P35', 'Beechcraft', 'Bonanza')
    add_model_alt('S35', 'Beechcraft', 'Bonanza')
    add_model_alt('V35', 'Beechcraft', 'Bonanza')
    add_model_alt('Baron', 'Beechcraft')
    add_model_alt('Bonanza', 'Beechcraft')
    add_model_alt('Duchess', 'Beechcraft')
    add_model_alt('Huron', 'Beechcraft')
    add_model_alt('King Air', 'Beechcraft')
    add_model_alt('Kingair', 'Beechcraft', 'King Air')
    add_model_alt('Premier I', 'Beechcraft')
    add_model_alt('Queen', 'Beechcraft')
    add_model_alt('707', 'Boeing')
    add_model_alt('717', 'Boeing')
    add_model_alt('720', 'Boeing')
    add_model_alt('727-1', 'Boeing')
    add_model_alt('727-2', 'Boeing')
    add_model_alt('727-200-O', 'Boeing')
    add_model_alt('737', 'Boeing', '737-1')
    add_model_alt('737-1', 'Boeing')
    add_model_alt('737-2', 'Boeing')
    add_model_alt('737-3', 'Boeing')
    add_model_alt('737-4', 'Boeing')
    add_model_alt('737-5', 'Boeing')
    add_model_alt('737-6', 'Boeing')
    add_model_alt('737-7', 'Boeing')
    add_model_alt('737-8', 'Boeing')
    add_model_alt('737-9', 'Boeing')
    add_model_alt('737-900ER', 'Boeing')
    add_model_alt('737-B', 'Boeing')
    add_model_alt('747-1', 'Boeing')
    add_model_alt('747-2', 'Boeing')
    add_model_alt('747-3', 'Boeing')
    add_model_alt('747-4', 'Boeing')
    add_model_alt('747-400ER', 'Boeing')
    add_model_alt('747-400-D', 'Boeing')
    add_model_alt('747-8', 'Boeing')
    add_model_alt('747-S', 'Boeing')
    add_model_alt('757-2', 'Boeing')
    add_model_alt('757-3', 'Boeing')
    add_model_alt('757-4', 'Boeing')
    add_model_alt('767-2', 'Boeing')
    add_model_alt('767-3', 'Boeing')
    add_model_alt('767-300ER', 'Boeing')
    add_model_alt('767-300-F', 'Boeing')
    add_model_alt('767-4', 'Boeing')
    add_model_alt('777-2', 'Boeing')
    add_model_alt('777-200LR', 'Boeing')
    add_model_alt('777-3', 'Boeing')
    add_model_alt('777-300ER', 'Boeing')
    add_model_alt('777-300F', 'Boeing')
    add_model_alt('777-4', 'Boeing')
    add_model_alt('777-F', 'Boeing', '777-3') # have same mtow
    add_model_alt('777F', 'Boeing', '777-3') # have same mtow
    add_model_alt('787-1', 'Boeing')
    add_model_alt('787-8', 'Boeing')
    add_model_alt('787-9', 'Boeing')
    add_model_alt('DC-10-1', 'Boeing')
    add_model_alt('DC-10-3', 'Boeing')
    add_model_alt('DC-10-4', 'Boeing')
    add_model_alt('DC-3', 'Boeing')
    add_model_alt('DC-4', 'Boeing')
    add_model_alt('DC-6', 'Boeing')
    add_model_alt('DC-7', 'Boeing')
    add_model_alt('DC-8', 'Boeing')
    add_model_alt('DC-8-1', 'Boeing')
    add_model_alt('DC-8-2', 'Boeing')
    add_model_alt('DC-8-3', 'Boeing')
    add_model_alt('DC-8-4', 'Boeing')
    add_model_alt('DC-8-5', 'Boeing')
    add_model_alt('DC-8-6', 'Boeing')
    add_model_alt('DC-8-7', 'Boeing')
    add_model_alt('DC-9-1', 'Boeing')
    add_model_alt('DC-9-2', 'Boeing')
    add_model_alt('DC-9-3', 'Boeing')
    add_model_alt('DC-9-4', 'Boeing')
    add_model_alt('DC-9-5', 'Boeing')
    add_model_alt('DC-9-8', 'Boeing')
    add_model_alt('KC-135', 'Boeing')
    add_model_alt('MD-11', 'Boeing')
    add_model_alt('MD-8', 'Boeing')
    add_model_alt('MD-81', 'Boeing')
    add_model_alt('MD-82', 'Boeing')
    add_model_alt('MD-83', 'Boeing')
    add_model_alt('MD-87', 'Boeing')
    add_model_alt('MD-9', 'Boeing')
    add_model_alt('BD-100-1A1', 'Bombardier')
    add_model_alt('BD-700-1A11', 'Bombardier', 'Global 5000')
    add_model_alt('BD-700-1A10', 'Bombardier', 'Global 6000')
    add_model_alt('BD-700-2A1', 'Bombardier', 'Global 7000')
    add_model_alt('Global 5000', 'Bombardier')
    add_model_alt('Global 6000', 'Bombardier')
    add_model_alt('Global Express', 'Bombardier', 'Global 6000')
    add_model_alt('Global 7000', 'Bombardier')
    add_model_alt('Global 8000', 'Bombardier')
    add_model_alt('Challenger 300', 'Bombardier', 'BD-100-1A1')
    add_model_alt('Challenger 350', 'Bombardier', 'BD-100-1A1')
    add_model_alt('Challenger 600', 'Bombardier', 'CL-600-1A11')
    add_model_alt('Challenger 601', 'Bombardier', 'CL-600-2A12')
    add_model_alt('Challenger 604', 'Bombardier', 'CL-600-2B16')
    add_model_alt('Challenger 650', 'Bombardier')
    add_model_alt('CL-215', 'Bombardier')
    add_model_alt('CL-415', 'Bombardier')
    add_model_alt('CL-600-1A11', 'Bombardier')
    add_model_alt('CL-600-2A12', 'Bombardier')
    add_model_alt('CL-600-2B16', 'Bombardier')
    add_model_alt('CL-600-2B19', 'Bombardier', 'CRJ 200')
    add_model_alt('CRJ 100/200', 'Bombardier', 'CRJ 200')
    add_model_alt('CRJ 100', 'Bombardier', 'CRJ 200')
    add_model_alt('CRJ 200', 'Bombardier')
    add_model_alt('CRJ 700', 'Bombardier')
    add_model_alt('CRJ 900', 'Bombardier')
    add_model_alt('CRJ 1000', 'Bombardier')
    add_model_alt('DHC-1', 'Bombardier')
    add_model_alt('DHC-104', 'Bombardier')
    add_model_alt('DHC-106', 'Bombardier')
    add_model_alt('DHC-114', 'Bombardier')
    add_model_alt('DHC-2', 'Bombardier')
    add_model_alt('DHC-3', 'Bombardier')
    add_model_alt('DHC-4', 'Bombardier')
    add_model_alt('DHC-5', 'Bombardier')
    add_model_alt('DHC-6-', 'Bombardier')
    add_model_alt('DHC-6-3', 'Bombardier')
    add_model_alt('DHC-7-10', 'Bombardier')
    add_model_alt('DHC-7-15', 'Bombardier')
    add_model_alt('DHC-8-101', 'Bombardier')
    add_model_alt('DHC-8-102', 'Bombardier')
    add_model_alt('DHC-8-103', 'Bombardier')
    add_model_alt('DHC-8-106', 'Bombardier')
    add_model_alt('DHC-8-2', 'Bombardier')
    add_model_alt('DHC-8-301', 'Bombardier')
    add_model_alt('DHC-8-31', 'Bombardier')
    add_model_alt('DHC-8-311', 'Bombardier')
    add_model_alt('DHC-8-4', 'Bombardier')
    add_model_alt('Q400', 'Bombardier')
    add_model_alt('Learjet 31', 'Bombardier')
    add_model_alt('Learjet 35', 'Bombardier')
    add_model_alt('Learjet 40', 'Bombardier')
    add_model_alt('Learjet 45', 'Bombardier')
    add_model_alt('Learjet 55', 'Bombardier')
    add_model_alt('Learjet 60', 'Bombardier')
    add_model_alt('CL-44', 'Bombardier')
    add_model_alt('One-Eleven 2', 'British Aircraft')
    add_model_alt('One-Eleven 3', 'British Aircraft')
    add_model_alt('One-Eleven 4', 'British Aircraft', 'One-Eleven 3')
    add_model_alt('One-Eleven 47', 'British Aircraft')
    add_model_alt('One-Eleven 5', 'British Aircraft')
    add_model_alt('RJ70', 'British Aerospace')
    add_model_alt('RJ85', 'British Aerospace')
    add_model_alt('RJ100', 'British Aerospace')
    add_model_alt('146-1', 'British Aerospace')
    add_model_alt('146-2', 'British Aerospace')
    add_model_alt('146-3', 'British Aerospace')
    add_model_alt('Lancaster', 'British Aerospace')
    add_model_alt('BN-2A', 'Britten-Norman')
    add_model_alt('BN-2T', 'Britten-Norman')
    add_model_alt('120', 'Cessna', '140')
    add_model_alt('140', 'Cessna')
    add_model_alt('150', 'Cessna')
    add_model_alt('152', 'Cessna')
    add_model_alt('162', 'Cessna')
    add_model_alt('165', 'Cessna')
    add_model_alt('170', 'Cessna')
    add_model_alt('172', 'Cessna')
    add_model_alt('175', 'Cessna')
    add_model_alt('177', 'Cessna')
    add_model_alt('180', 'Cessna')
    add_model_alt('182', 'Cessna')
    add_model_alt('185', 'Cessna')
    add_model_alt('188', 'Cessna')
    add_model_alt('190', 'Cessna')
    add_model_alt('205', 'Cessna')
    add_model_alt('206', 'Cessna')
    add_model_alt('207', 'Cessna')
    add_model_alt('208', 'Cessna')
    add_model_alt('210', 'Cessna')
    add_model_alt('303', 'Cessna')
    add_model_alt('310', 'Cessna')
    add_model_alt('318', 'Cessna')
    add_model_alt('320', 'Cessna')
    add_model_alt('335', 'Cessna')
    add_model_alt('336', 'Cessna')
    add_model_alt('337', 'Cessna')
    add_model_alt('340', 'Cessna')
    add_model_alt('350', 'Cessna')
    add_model_alt('400', 'Cessna')
    add_model_alt('401', 'Cessna')
    add_model_alt('402', 'Cessna')
    add_model_alt('404', 'Cessna')
    add_model_alt('411', 'Cessna')
    add_model_alt('414', 'Cessna')
    add_model_alt('421', 'Cessna')
    add_model_alt('425', 'Cessna')
    add_model_alt('441', 'Cessna')
    add_model_alt('501', 'Cessna')
    add_model_alt('510', 'Cessna')
    add_model_alt('525', 'Cessna')
    add_model_alt('525A', 'Cessna')
    add_model_alt('525B', 'Cessna')
    add_model_alt('525C', 'Cessna')
    add_model_alt('550', 'Cessna')
    add_model_alt('560', 'Cessna',)
    add_model_alt('680', 'Cessna')
    add_model_alt('CJ1', 'Cessna', '525')
    add_model_alt('CJ2', 'Cessna', '525A')
    add_model_alt('CJ3', 'Cessna', '525B')
    add_model_alt('CJ4', 'Cessna', '525C')
    add_model_alt('Bravo', 'Cessna', '550')
    add_model_alt('Citation II', 'Cessna', '550')
    add_model_alt('Citation III', 'Cessna')
    add_model_alt('Citation V', 'Cessna')
    add_model_alt('Citation VI', 'Cessna', 'Citation III')
    add_model_alt('Citation X', 'Cessna')
    add_model_alt('Excel', 'Cessna', '560')
    add_model_alt('Encore', 'Cessna')
    add_model_alt('Latitude', 'Cessna')
    add_model_alt('M2', 'Cessna')
    add_model_alt('Mustang', 'Cessna', '510')
    add_model_alt('Sovereign', 'Cessna', '680')
    add_model_alt('XLS', 'Cessna')
    add_model_alt('SF50', 'Cirrus')
    add_model_alt('SR20', 'Cirrus')
    add_model_alt('SR22', 'Cirrus')
    add_model_alt('21-7', 'Comac')
    add_model_alt('21-9', 'Comac')
    add_model_alt('919', 'Comac')
    add_model_alt('919ER', 'Comac', '919')
    add_model_alt('919 ER', 'Comac', '919')
    add_model_alt('240', 'Convair')
    add_model_alt('340', 'Convair')
    add_model_alt('440', 'Convair')
    add_model_alt('580', 'Convair')
    add_model_alt('880', 'Convair')
    add_model_alt('990', 'Convair')
    add_model_alt('Coronado', 'Convair', '990')
    add_model_alt('TB-10', 'Daher')
    add_model_alt('TB-2', 'Daher')
    add_model_alt('TB-30', 'Daher')
    add_model_alt('TBM-700', 'Daher')
    add_model_alt('TBM-850', 'Daher')
    add_model_alt('TBM-900', 'Daher')
    add_model_alt('Alpha', 'Dassault')
    add_model_alt('Falcon 10', 'Dassault')
    add_model_alt('Falcon 20', 'Dassault')
    add_model_alt('Falcon 50', 'Dassault')
    add_model_alt('Falcon 6X', 'Dassault')
    add_model_alt('Falcon 7X', 'Dassault')
    add_model_alt('Falcon 8X', 'Dassault')
    add_model_alt('Falcon 900B', 'Dassault')
    add_model_alt('Falcon 900', 'Dassault', 'Falcon 900B')
    add_model_alt('Falcon 900C', 'Dassault', 'Falcon 900B')
    add_model_alt('Falcon 900D', 'Dassault')
    add_model_alt('Falcon 900E', 'Dassault')
    add_model_alt('Falcon 900L', 'Dassault')
    add_model_alt('Falcon 2000', 'Dassault')
    add_model_alt('Falcon 2000E', 'Dassault')
    add_model_alt('Falcon 2000S', 'Dassault')
    add_model_alt('Falcon 2000L', 'Dassault')
    add_model_alt('Falcon 2000X', 'Dassault', 'Falcon 2000L')
    add_model_alt('Mercure', 'Dassault')
    add_model_alt('Mirage 2', 'Dassault')
    add_model_alt('Mystere', 'Dassault')
    add_model_alt('DA-20', 'Diamond')
    add_model_alt('DA-40', 'Diamond')
    add_model_alt('DA-42', 'Diamond')
    add_model_alt('DA-50', 'Diamond')
    add_model_alt('DA-62', 'Diamond')
    add_model_alt('HK36', 'Diamond')
    add_model_alt('Do 128', 'Dornier')
    add_model_alt('Do 228', 'Dornier')
    add_model_alt('Do 27', 'Dornier')
    add_model_alt('Do 28', 'Dornier')
    add_model_alt('Do 328', 'Dornier')
    add_model_alt('EA50', 'Eclipse')
    add_model_alt('500', 'Eclipse', 'EA500')
    add_model_alt('EMB-11', 'Embraer')
    add_model_alt('EMB-120', 'Embraer')
    add_model_alt('EMB-121', 'Embraer')
    add_model_alt('EMB-135', 'Embraer')
    add_model_alt('EMB-140', 'Embraer')
    add_model_alt('EMB-145', 'Embraer')
    add_model_alt('EMB-170', 'Embraer')
    add_model_alt('EMB-175', 'Embraer')
    add_model_alt('EMB-175-E2', 'Embraer')
    add_model_alt('EMB-190', 'Embraer')
    add_model_alt('EMB-190-E2', 'Embraer')
    add_model_alt('E195', 'Embraer','EMB-195')
    add_model_alt('EMB-195', 'Embraer')
    add_model_alt('EMB-195-E2', 'Embraer')
    add_model_alt('EMB-500', 'Embraer')
    add_model_alt('EMB-505', 'Embraer')
    add_model_alt('Legacy 450', 'Embraer')
    add_model_alt('Legacy 500', 'Embraer')
    add_model_alt('Legacy 600', 'Embraer')
    add_model_alt('Legacy 650', 'Embraer')
    add_model_alt('Phenom 100', 'Embraer', 'EMB-500')
    add_model_alt('Phenom 300', 'Embraer', 'EMB-505')
    add_model_alt('CT', 'Flight Design')
    add_model_alt('27-5', 'Fokker')
    add_model_alt('28-1', 'Fokker')
    add_model_alt('28-2', 'Fokker')
    add_model_alt('28-3', 'Fokker')
    add_model_alt('28-4', 'Fokker')
    add_model_alt('28-6', 'Fokker')
    add_model_alt('614', 'Fokker')
    add_model_alt('VFW', 'Fokker', '614')
    add_model_alt('Sportsman', 'Glasair')
    add_model_alt('Sportsman 2+2', 'Glasair')
    add_model_alt('G100', 'Gulfstream')
    add_model_alt('G150', 'Gulfstream')
    add_model_alt('G159', 'Gulfstream')
    add_model_alt('G200', 'Gulfstream')
    add_model_alt('G280', 'Gulfstream')
    add_model_alt('G300', 'Gulfstream')
    add_model_alt('G350', 'Gulfstream')
    add_model_alt('G400', 'Gulfstream')
    add_model_alt('G450', 'Gulfstream')
    add_model_alt('G500', 'Gulfstream')
    add_model_alt('G550', 'Gulfstream')
    add_model_alt('G600', 'Gulfstream')
    add_model_alt('G650', 'Gulfstream')
    add_model_alt('GI', 'Gulfstream', 'G159')
    add_model_alt('GII', 'Gulfstream')
    add_model_alt('GIII', 'Gulfstream')
    add_model_alt('GIV', 'Gulfstream', 'G400')
    add_model_alt('GIV', 'Gulfstream', 'G400')
    add_model_alt('GV', 'Gulfstream')
    add_model_alt('GVI', 'Gulfstream', 'G650')
    add_model_alt('G I', 'Gulfstream', 'G159')
    add_model_alt('G II', 'Gulfstream')
    add_model_alt('G III', 'Gulfstream')
    add_model_alt('G IV', 'Gulfstream', 'G400')
    add_model_alt('G IV', 'Gulfstream', 'G400')
    add_model_alt('G V', 'Gulfstream')
    add_model_alt('G VI', 'Gulfstream', 'G650')
    add_model_alt('IL-12', 'Ilyushin')
    add_model_alt('IL-18', 'Ilyushin')
    add_model_alt('IL-62', 'Ilyushin')
    add_model_alt('IL-76', 'Ilyushin')
    add_model_alt('IL-86', 'Ilyushin')
    add_model_alt('IL-96', 'Ilyushin')
    add_model_alt('Astra', 'Israel')
    add_model_alt('Comm', 'Israel')
    add_model_alt('Westwind', 'Israel')
    add_model_alt('1329', 'Lockheed')
    add_model_alt('Jetstar', 'Lockheed', '1329')
    add_model_alt('1011-1', 'Lockheed')
    add_model_alt('1011-2', 'Lockheed')
    add_model_alt('1011-25', 'Lockheed')
    add_model_alt('1011-15', 'Lockheed')
    add_model_alt('C-130', 'Lockheed')
    add_model_alt('C-130J', 'Lockheed')
    add_model_alt('C-141', 'Lockheed')
    add_model_alt('C-5B', 'Lockheed')
    add_model_alt('P-3', 'Lockheed')
    add_model_alt('M10', 'Mooney')
    add_model_alt('M18', 'Mooney')
    add_model_alt('M.20', 'Mooney', 'M20')
    add_model_alt('M20', 'Mooney')
    add_model_alt('M22', 'Mooney')
    add_model_alt('P.68C', 'Partenavia')
    add_model_alt('P-180', 'Piaggio')
    add_model_alt('PD-808', 'Piaggio')
    add_model_alt('PC-6', 'Pilatus')
    add_model_alt('PC-12', 'Pilatus')
    add_model_alt('PC-XII', 'Pilatus', 'PC-12')
    add_model_alt('PC-24', 'Pilatus')
    add_model_alt('J-3', 'Piper')
    add_model_alt('J3C', 'Piper', 'J-3')
    add_model_alt('PA-18', 'Piper')
    add_model_alt('PA-24', 'Piper')
    add_model_alt('PA-28', 'Piper')
    add_model_alt('PA-31', 'Piper')
    add_model_alt('PA-32', 'Piper')
    add_model_alt('PA-34', 'Piper')
    add_model_alt('PA-36', 'Piper')
    add_model_alt('PA-38', 'Piper')
    add_model_alt('PA-39', 'Piper')
    add_model_alt('PA-42', 'Piper')
    add_model_alt('PA-44', 'Piper')
    add_model_alt('PA-46', 'Piper')
    add_model_alt('PA-6', 'Piper')
    add_model_alt('680', 'Rockwell')
    add_model_alt('690', 'Rockwell')
    add_model_alt('695', 'Rockwell')
    add_model_alt('B-1', 'Rockwell')
    add_model_alt('Guppy', 'Spacelines')
    add_model_alt('377', 'Spacelines', 'Guppy')
    add_model_alt('10', 'Stinson')
    add_model_alt('Voyager', 'Stinson', '10')
    add_model_alt('108', 'Stinson')
    add_model_alt('Reliant', 'Stinson')
    add_model_alt('Tri', 'Stinson')

    return df
