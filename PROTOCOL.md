# HA<==>HAOSS
> socket(request/response[optional])

1. register  

	- request
	
	field    |type  |length|notes
	-----    |----  |------|-----
	action   |string|4     |'REGI'
	mac      |string|17    |
	
	- response
    
	field    |type  |length|notes
	-----    |----  |------|-----
	action   |string|4     |'RPRE'
	status   |string|4     |1. 'OK'，right fill ' '  <br>2. 'FAIL'
	comm_code|string|40    |

2. logout

	- request
	
	field    |type  |length|notes
	-----    |----  |------|-----
	action   |string|4     |'LOGO'
	mac      |string|17    |

   - response
   
	field    |type  |length|notes
	-----    |----  |------|-----
	action   |string|4     |'RPLO'
	status   |string|4     |1. 'OK'，right fill ' '<br>2. 'FAIL'
	

3. keep-live(no response)

	field    |type  |length|notes
	-----    |----  |------|-----
	action   |string|4     |'KEEP'
	mac      |string|17    |
