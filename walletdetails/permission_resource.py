

PERMISSION = {'USER':
                  {
                      'POST':['/transfer/getBalance' , '/transfer/getTransaction','/transfer/transferFund'],
                      'GET': []
                  },
              'ADMIN':
                  {
                      'POST': ['/transfer/getBalance' , '/transfer/getTransaction' , '/transfer/transferFund', '/transfer/getResourceUsage'],
                      'GET': []
                  },
              'SUPER_USER':
                    {
                        'POST': ['/transfer/getBalance' , '/transfer/getTransaction', '/transfer/transferFund', '/transfer/getResourceUsage', 'wallet/adduser', 'wallet/changeuser'],
                        'GET': []
                    }

}