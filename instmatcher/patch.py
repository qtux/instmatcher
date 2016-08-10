import pycountry

def patch_getter():
	old_getter = pycountry.countries.get
	if old_getter.__name__ == 'new_getter':
		return
	data_class = type(
		pycountry.ExistingCountries.data_class_name,
		(pycountry.db.Data,),
		{}
	)
	kosovo_dict = {
		'alpha2': 'XK',
		'alpha3': 'UNK',
		'name': 'Kosovo',
		'official_name': 'Republic of Kosovo',
	}
	def new_getter(*args, **kw):
		try:
			return old_getter(*args, **kw)
		except KeyError as error:
			for key, value in kw.items():
				if (key, value) in kosovo_dict.items():
					return data_class(None, **kosovo_dict)
			raise error
	pycountry.countries.get = new_getter

patch_getter()
